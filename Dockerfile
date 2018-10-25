ARG DOCKER_NOTEBOOK_IMAGE=jupyter/minimal-notebook:e1677043235c
FROM kwarc/mmt:devel AS mmt
FROM $DOCKER_NOTEBOOK_IMAGE

ARG JUPYTERHUB_VERSION=0.8.0

USER root

# Install java
RUN apt-get update && apt-get install -y openjdk-8-jre-headless && apt-get clean

# Install MMT
RUN mkdir -p /mmt/
COPY --from=mmt /mmt/deploy/mmt.jar /mmt/mmt.jar
ENV MMT_JAR_LOCATION="/mmt/mmt.jar"
ENV MMT_MSL_LOCATION="/mmt/startup.msl"
ADD startup.msl /mmt/startup.msl

# Add MMT kernel
ADD mmt_kernel mmt_jupyter_kernel/mmt_kernel
ADD setup.py mmt_jupyter_kernel/setup.py

RUN python3 -m pip install --no-cache jupyterhub==${JUPYTERHUB_VERSION} \
    && python3 -m pip install py4j ipywidgets \
    && jupyter nbextension enable --py widgetsnbextension --sys-prefix\
    && cd mmt_jupyter_kernel && pip install . && python3 -m mmt_kernel.install && cd .. && rm -rf mmt_jupyter_kernel \
    
    && git clone https://github.com/kwarc/jupyter-console-standalone && cd jupyter-console-standalone/jcs/files && npm install && npm run build && cd ../../ \
    && python setup.py install && jupyter serverextension enable --sys-prefix --py jcs && cd .. \
    && rm -rf jupyter-console-standalone \
    
    && git clone https://github.com/KWARC/jupyter-upload-handler && cd jupyter-upload-handler \
    && python setup.py install && jupyter serverextension enable --sys-prefix --py juh && cd .. \
    && rm -rf jupyter-upload-handler
