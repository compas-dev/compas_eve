********************************************************************************
Installation
********************************************************************************

.. highlight:: bash

**COMPAS EVE** can be easily installed on multiple platforms,
using popular package managers such as conda or pip.

Install with conda
==================

The recommended way to install **COMPAS EVE** is with `conda <https://conda.io/docs/>`_.
For example, create an environment named ``project_name`` and install ``compas_eve``.

::

    conda create -n project_name -c conda-forge compas_eve

Afterwards, simply activate the environment and run the following
command to check if the installation process was successful.

.. code-block:: bash

    conda activate project_name
    python -m compas_eve

.. code-block:: none

    COMPAS EVE v1.0.0 is installed!

You are ready to use **COMPAS EVE**!

Installation options
--------------------

Install COMPAS EVE in an environment with a specific version of Python.

.. code-block:: bash

    conda create -n project_name python=3.8 compas_eve

Install COMPAS EVE in an existing environment.

.. code-block:: bash

    conda install -n project_name compas_eve

Install with pip
================

Install COMPAS EVE using ``pip`` from the Python Package Index.

.. code-block:: bash

    pip install compas_eve

Install an editable version from local source.

.. code-block:: bash

    cd path/to/compas_eve
    pip install -e .

Note that installation with ``pip`` is also possible within a ``conda`` environment.

.. code-block:: bash

    conda activate project_name
    pip install -e .


Update with conda
=================

To update COMPAS EVE to the latest version with ``conda``

.. code-block:: bash

    conda update compas_eve

To switch to a specific version

.. code-block:: bash

    conda install compas_eve=1.0.0


Update with pip
===============

If you installed COMPAS EVE with ``pip`` the update command is the following

.. code-block:: bash

    pip install --upgrade compas_eve

Or to switch to a specific version

.. code-block:: bash

    pip install compas_eve==1.0.0


Working in Rhino
================

To make **COMPAS EVE** available inside Rhino, open the *command prompt*,
activate the appropriate environment, and type the following:

::

    python -m compas_rhino.install

Open Rhino, start the Python script editor, type ``import compas_eve`` and
run it to verify that your installation is working.

