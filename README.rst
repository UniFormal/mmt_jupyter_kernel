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
    extension info.kwarc.mmt.interviews.InterviewServer

Start a Jupyter notebook with::

    jupyter notebook

Select the ``mmt_kernel`` as Kernel in your notebook.
Now you can enter following commands in your Jupyter console::

    create view <V> <fromTheory> <toTheory>
    create theory <T> [<metaTheory>]
    add term <Term>
    add declaration <Decl>
    show metaTheory
    show namespace
    show scope
    set metaTheory <MetaTheory>
    set namespace <Namespace>

In case you make any modifications redo ``python setup.py install`` before starting a notebook
