FROM bentoml/model-server:0.11.0-py37
MAINTAINER ersilia

RUN conda install -c conda-forge rdkit
RUN pip install torch
RUN pip install numpy
RUN pip install tqdm
RUN pip install scipy
RUN pip install sklearn
RUN pip install git+https://github.com/bp-kelley/descriptastorus

WORKDIR /repo
COPY . /repo
