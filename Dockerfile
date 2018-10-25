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
ENV MMT_MSL_LOCATION="/mmt/notstartup.msl"
ADD startup.msl /mmt/notstartup.msl

# Install jupyterhub
RUN pip install --no-cache jupyterhub==${JUPYTERHUB_VERSION} && \
    pip install py4j ipywidgets && \
    jupyter nbextension enable --py widgetsnbextension --sys-prefix

# Install MMT_JUPYTER KERNEL
RUN mkdir -p /deps/mmt_jupyter_kernel
ADD mmt_kernel /deps/mmt_jupyter_kernel/mmt_kernel
ADD setup.py /deps/mmt_jupyter_kernel/setup.py
ADD README.md /deps/mmt_jupyter_kernel/README.md
RUN pip install /deps/mmt_jupyter_kernel && cd /deps/mmt_jupyter_kernel/ && python3 -m mmt_kernel.install

# Install jupyter console standalone
RUN git clone https://github.com/kwarc/jupyter-console-standalone /deps/jupyter-console-standalone && \
    cd /deps/jupyter-console-standalone/jcs/files  && npm install && npm run build && \
    pip install /deps/jupyter-console-standalone && jupyter serverextension enable --sys-prefix --py jcs && \
    rm -rf /deps/jupyter-console-standalone


# Install jupyter upload handler
ENV UPLOAD_REDIRECT_PREFIX="/user-redirect"
RUN git clone https://github.com/KWARC/jupyter-upload-handler /deps/jupyter-upload-handler && \
    pip install /deps/jupyter-upload-handler && jupyter serverextension enable --sys-prefix --py juh  && \
    rm -rf /deps/jupyter-upload-handler
