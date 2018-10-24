mmt_juypter_kernel
===========

``mmt_jupyter_kernel`` is a MMT kernel

Prerequisites
-------------
for the ``mmt_jupyter_kernel`` to run, install [Py4J](https://www.py4j.org/) and [ipywidgets](https://ipywidgets.readthedocs.io/en/latest/) first:

    pip install py4j
    pip install ipywidgets

if you haven't installed the ``requests`` module run:

    pip install requests

and enable the widgets in your Notebooks:

    jupyter nbextension enable --py widgetsnbextension --sys-prefix\


Installation
------------
To install ``mmt_jupyter_kernel`` with PyPI:

    git clone https://github.com/UniFormal/mmt_jupyter_kernel.git
    pip install mmt_jupyter_kernel
    cd mmt_jupyter_kernel
    python setup.py install
    python -m mmt_kernel.install

Usage
-----
In the MMT Shell:

    server on port 9000
    extension info.kwarc.mmt.python.Py4JGateway
    extension info.kwarc.mmt.api.web.REPLServer

Start a Jupyter notebook with:

    jupyter notebook

Select the ``mmt__jupyter_kernel`` as Kernel in your notebook.
Now you can enter MMT surface syntax as you would in JEdit.

In case you make any modifications redo ``python setup.py install`` before starting a notebook.
This package works on Python 3 only.
