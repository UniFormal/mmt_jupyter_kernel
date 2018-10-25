ARG DOCKER_NOTEBOOK_IMAGE=jupyter/minimal-notebook:e1677043235c
FROM kwarc/mmt:devel AS mmt
FROM $DOCKER_NOTEBOOK_IMAGE
ARG JUPYTERHUB_VERSION=0.8.0

COPY --from=mmt /mmt/deploy/mmt.jar ./mmt.jar
ENV MMT_JAR_LOCATION="./mmt.jar"
ENV MMT_MSL_LOCATION="./s.msl"
ADD startup.msl s.msl
ADD mmt_kernel mmt_jupyter_kernel/mmt_kernel
ADD setup.py mmt_jupyter_kernel/setup.py
ADD README.md mmt_jupyter_kernel/README.md

USER root 
RUN apt-get update && apt-get install -y openjdk-8-jre-headless && apt-get clean
RUN python3 -m pip install --no-cache jupyterhub==${JUPYTERHUB_VERSION} \
    && pip install py4j \
    && pip install ipywidgets \
    && jupyter nbextension enable --py widgetsnbextension --sys-prefix\
    && cd mmt_jupyter_kernel \
    && pip install . \
    && cd mmt_kernel \
    && python3 install.py \
    && cd .. \
    && python3 -m mmt_kernel.install \
    && cd .. && rm -rf mmt_jupyter_kernel \
    && git clone https://github.com/kwarc/jupyter-console-standalone \
    && cd jupyter-console-standalone/jcs/files && npm install && npm run build && cd ../../ \
    && python setup.py install && jupyter serverextension enable --sys-prefix --py jcs && cd .. \
    && rm -rf jupyter-console-standalone
