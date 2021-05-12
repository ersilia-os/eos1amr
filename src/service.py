from bentoml import BentoService, api, artifacts
from bentoml.adapters import JsonInput
from bentoml.types import JsonSerializable
from typing import List

import shutil
import os
import csv
import tempfile
import subprocess
import pickle

from bentoml.service import BentoServiceArtifact

CHECKPOINTS_BASEDIR = "BBBPbase"
FRAMEWORK_BASEDIR = "framework"

MODEL_NAME = "model"


def load_model(framework_dir, checkpoints_dir):
    mdl = Model()
    mdl.load(framework_dir, checkpoints_dir)
    return mdl


class Model(object):
    def __init__(self):
        self.DATA_FILE = "data.csv"
        self.FEAT_FILE = "features.npz"
        self.PRED_FILE = "pred.csv"
        self.RUN_FILE = "run.sh"

    def load(self, framework_dir, checkpoints_dir):
        self.framework_dir = framework_dir
        self.checkpoints_dir = checkpoints_dir

    def set_checkpoints_dir(self, dest):
        self.checkpoints_dir = os.path.abspath(dest)

    def set_framework_dir(self, dest):
        self.framework_dir = os.path.abspath(dest)

    def read_columns(self):
        self.columns = []
        with open(os.path.join(self.framework_dir, "columns.txt"), "r") as f:
            for l in f:
                l = l.rstrip()
                if l:
                    self.columns += [l]

    def predict(self, smiles_list):
        self.read_columns()
        tmp_folder = tempfile.mkdtemp()
        data_file = os.path.join(tmp_folder, self.DATA_FILE)
        feat_file = os.path.join(tmp_folder, self.FEAT_FILE)
        pred_file = os.path.join(tmp_folder, self.PRED_FILE)
        with open(data_file, "w") as f:
            f.write(",".join(["smiles"] + self.columns) + os.linesep)
            for smiles in smiles_list:
                f.write(",".join([smiles] + ["0"]*len(self.columns)) + os.linesep)
        run_file = os.path.join(tmp_folder, self.RUN_FILE)
        with open(run_file, "w") as f:
            lines = ["export KMP_DUPLICATE_LIB_OK=TRUE"]
            lines += [
                "python {0}/save_features.py --data_path {1} --save_path {2} --features_generator rdkit_2d_normalized --restart".format(
                    self.framework_dir, data_file, feat_file
                )
            ]
            lines += [
                "python {0}/predict.py predict --data_path {1} --features_path {2} --checkpoint_dir {3} --no_features_scaling --output {4}".format(
                    self.framework_dir,
                    data_file,
                    feat_file,
                    self.checkpoints_dir,
                    pred_file,
                )
            ]
            f.write(os.linesep.join(lines))
        cmd = "bash {0}".format(run_file)
        with open(os.devnull, "w") as fp:
            subprocess.Popen(
                cmd, stdout=fp, stderr=fp, shell=True, env=os.environ
            ).wait()
        with open(pred_file, "r") as f:
            reader = csv.reader(f)
            h = next(reader)
            result = []
            for r in reader:
                pred = {}
                for i, col in enumerate(h):
                    if i == 0: continue
                    pred[col] = float(r[i])
                result += [pred]
        return result


class Artifact(BentoServiceArtifact):
    """Dummy  artifact to deal with file locations of checkpoints"""

    def __init__(self, name):
        super(Artifact, self).__init__(name)
        self._model = None
        self._extension = ".pkl"

    def _copy_checkpoints(self, base_path):
        src_folder = self._model.checkpoints_dir
        dst_folder = os.path.join(base_path, "checkpoints")
        if os.path.exists(dst_folder):
            os.rmdir(dst_folder)
        shutil.copytree(src_folder, dst_folder)

    def _copy_framework(self, base_path):
        src_folder = self._model.framework_dir
        dst_folder = os.path.join(base_path, "framework")
        if os.path.exists(dst_folder):
            os.rmdir(dst_folder)
        shutil.copytree(src_folder, dst_folder)

    def _model_file_path(self, base_path):
        return os.path.join(base_path, self.name + self._extension)

    def pack(self, model):
        self._model = model
        return self

    def load(self, path):
        model_file_path = self._model_file_path(path)
        model = pickle.load(open(model_file_path, "rb"))
        model.set_checkpoints_dir(
            os.path.join(os.path.dirname(model_file_path), "checkpoints")
        )
        model.set_framework_dir(
            os.path.join(os.path.dirname(model_file_path), "framework")
        )
        return self.pack(model)

    def get(self):
        return self._model

    def save(self, dst):
        self._copy_checkpoints(dst)
        self._copy_framework(dst)
        pickle.dump(self._model, open(self._model_file_path(dst), "wb"))


@artifacts([Artifact(MODEL_NAME)])
class Service(BentoService):
    @api(input=JsonInput(), batch=True)
    def predict(self, input: List[JsonSerializable]):
        input=input[0]
        smiles_list=[inp["input"] for inp in input]
        output = self.artifacts.model.predict(smiles_list)
        return[output]
