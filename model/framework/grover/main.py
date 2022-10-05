import random
import sys
import os
import numpy as np
import torch
import pandas as pd
from rdkit import RDLogger
from pathlib import Path
import tempfile

from grover.util.parsing import parse_args, get_newest_train_args
from grover.util.utils import create_logger
from task.cross_validate import cross_validate
from task.fingerprint import generate_fingerprints
from task.predict import make_predictions, write_prediction
from task.pretrain import pretrain_model
from grover.data.torchvocab import MolVocab
import scripts.save_features as sf

class Namespace:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

def setup(seed):
    # frozen random seed
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    np.random.seed(seed)
    random.seed(seed)
    torch.backends.cudnn.deterministic = True

def smiles_to_dataframe(txt_file_path):

    
    df = pd.read_csv(txt_file_path, header=None,  names=['smiles'])
    
    dummy_labels = pd.Series(np.zeros(df.shape[0]))

    names =    ['p_np']
    
    for n in names:
        df[n] = dummy_labels.values

    input_csv_path = txt_file_path.split(".")[0] + ".csv"
    df.to_csv(input_csv_path, index=False)
    
    return input_csv_path

tmp_folder = tempfile.mktemp()
features_path = os.path.join(tmp_folder, "features.npz")    

if __name__ == '__main__':
    # setup random seed
    setup(seed=42)
    # Avoid the pylint warning.
    a = MolVocab
    # supress rdkit logger
    lg = RDLogger.logger()
    lg.setLevel(RDLogger.CRITICAL)

    # Initialize MolVocab
    mol_vocab = MolVocab

    input_txt_path =  sys.argv[1]
    output_path = sys.argv[2]
    csv_path = smiles_to_dataframe(input_txt_path)

    s = os.path.dirname(os.path.abspath(__file__))
    p = Path(s)
    model_path = str(p.parent.parent.absolute())

    args = Namespace(batch_size=32, checkpoint_dir=model_path+'/framework/finetune/bbbp', checkpoint_path=None, checkpoint_paths=[model_path+'/framework/finetune/bbbp/fold_0/model_0/model.pt', model_path+'/framework/finetune/bbbp/fold_2/model_0/model.pt', model_path+'/framework/finetune/bbbp/fold_1/model_0/model.pt'], cuda=False, data_path=csv_path, ensemble_size=3, features_generator=None, features_path=[features_path], fingerprint=False, gpu=0, no_cache=True, no_features_scaling=True, output_path=output_path, parser_name='predict')


    sf.save_features_main(csv_path, features_path)

    train_args = get_newest_train_args()
    avg_preds, test_smiles = make_predictions(args, train_args)
    write_prediction(avg_preds, test_smiles, args)

    os.remove(csv_path)
