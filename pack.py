from src.service import load_model
from src.service import Service
from src.service import CHECKPOINTS_BASEDIR, FRAMEWORK_BASEDIR, MODEL_NAME

import os

root = os.path.dirname(os.path.realpath(__file__))
mdl = load_model(
    os.path.join(root, "model", FRAMEWORK_BASEDIR),
    os.path.join(root, "model", CHECKPOINTS_BASEDIR),
)

service = Service()
service.pack(MODEL_NAME, mdl)
service.save()
