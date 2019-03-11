mmt_juypter_kernel
===========

`mmt_jupyter_kernel` is a MMT kernel for Jupyter. This repository is meant for local deployment of the kernel. For a production setup refer to the [deployment](https://github.com/KWARC/jupyterhub-mathhub-deploy-docker) version.

Prerequisites
-------------
This kernel uses MMT You can either build it from the [source](https://github.com/UniFormal/MMT) by following the [installation instructions](https://uniformal.github.io/doc/setup/), or simply download the `mmt.jar` from the latest [release](https://github.com/UniFormal/MMT/releases). We also recommend a [anaconda](https://www.anaconda.com) python distribution as it already contains most of the required packages.

Environment Variables
-------------

The kernel reads the following environment variables for configuration:

- `MMT_JAR_LOCATION` Location of the `mmt.jar`, defaults to `~/MMT/deploy/mmt.jar`. 
- `MMT_MSL_LOCATION` Location of starup msl file, defaults to `~/MMT/deploy/startup.msl`.
- `MMT_PY4J_HOST` IP Address (a hostname will not work) of Py4J MMT Server
- `MMT_PY4J_PORT` Port of an existing Py4J MMT Server to connect to

On startup, if the `MMT_PY4J_PORT` variable is set, the kernel will try to connect to an existing MMT Py4J host. 
If this is not given, it will instead spawn a new one using the `java` executable in `$PATH` using the provided `MMT_JAR_LOCATION` and `MMT_MSL_LOCATION`. 

Installation
------------
Clone the kernel:

    git clone https://github.com/UniFormal/mmt_jupyter_kernel.git
    cd mmt_jupyter_kernel

Install all necessary packages:

    pip install -r requirements.txt

and enable the [ipywidgets](https://ipywidgets.readthedocs.io/en/stable/) in your notebooks:

    jupyter nbextension enable --py widgetsnbextension

Configure your kernel with:

    ./configure

Finally install the kernel module with:

    python setup.py install
    python -m mmt_kernel.install
    

Usage
-----
You're now ready to go and can start a Jupyter notebook with:

    jupyter notebook

Select the `mmt__jupyter_kernel` as kernel in your notebook.
Now you can enter MMT surface syntax as you would in JEdit. Entering unicode characters works by simply typing their latex command and pressing `tab`.

In case you make any modifications redo `python setup.py install` before starting a notebook.
This package works on Python 3 only.
