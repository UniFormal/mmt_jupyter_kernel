mmt_kernel
===========

``mmt_kernel`` is a MMT kernel

Installation
------------
To install ``mmt_kernel`` from PyPI::

    pip install mmt_jupyter_kernel
    python setup.py install
    python -m mmt_kernel.install

Usage
-----
In the MMT Shell::

    server on port 9000
    extension info.kwarc.mmt.api.web.REPLServer

Start a Jupyter notebook with::

    jupyter notebook

Select the ``mmt_kernel`` as Kernel in your notebook.
Now you can enter MMT surface syntax as you would in JEdit

In case you make any modifications redo ``python setup.py install`` before starting a notebook
