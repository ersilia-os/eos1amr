# Blood-Brain Barrier Penetration

This model has been developed using GROVER, a Graph Neural Network pretrained with 10 million unlabelled molecules from ChEMBL and ZINC15. GROVER has then been fine-tuned to predict Blood Brain Barrier Penetration (BBBP) using the BBBP dataset curated by MoleculeNet. This dataset curates permeability information for 2000 molecules from scientific literature.
GROVER predictions consistently outperformed other state-of-the-art methods for Lipo and other benchmark datasets from [MoleculeNet](https://pubs.rsc.org/en/content/articlelanding/2018/sc/c7sc02664a#!divAbstract).
## Summary
* Predicts **Blood-Brain Barrier Penetration** for small molecules
* Takes **compound structures** as input
* Trained with the benchmark **BBBP MoleculeNet** dataset (2039 molecules)
* Results validated **in-silico** against baseline methods for the same dataset
* Published in [*Rong et al, Advances in Neural Information Processing Systems 2020*](https://papers.nips.cc/paper/2020/hash/94aef38441efa3380a3bed3faf1f9d5d-Abstract.html)
* Processed data can be found [here](https://github.com/tencent-ailab/grover)

## Specifications
* Input: SMILES string (also accepts an InChIKey string or a molecule name string, and converts them to SMILES)
* Endpoint: BBB permeability
* Results interpretation: 0: not permeable - 1: highly permeable

## History
1. Model was downloaded on 06.05.21 from [TencentAILab](https://github.com/tencent-ailab/grover)
2. We duplicated task/predict.py and scripts/save_features.py from Tencent GitHub repository
3. Model was incorporated to Ersilia on 11/05/2021
