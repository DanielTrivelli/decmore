.. _getting_started:

Getting started
===============

Requirements
------------

* Python (3.7, 3.8, 3.9, 3.10)

Installation
------------

DecMore can be installed with pip:

.. code-block:: console

  pip install decmore




Usage
-----

To use the decorators, simply import the library into the desired ``.py`` file and place them in the functions or classes:

.. code-block:: python

    from decmore import CheckTypes

    @CheckTypes()
    def test_function(var1: str, var2: list, var: int):
        ...