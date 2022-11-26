.. _decorators:

Base
===============

The Base decorator is only meant to help other useful decorators, so it should not be used as a decorator for your code.
If you want to understand more about it locate the file ``default.py``
With its implementation we can tell the decorators what properties, features and changes they should support

.. code-block:: python

    class BaseDecorator(object):
        allowed_params = []
        allowed_methods = []
        disallowed_methods = []
        class_injection = True
        instance: Callable | None = None
        _traced_methods = {}
        is_class = False


``allowed_params``
-------------------------
This property, which is in WIP, will allow you to restrict the parameters passed to each decorator


``allowed_methods``
-------------------------
This property is sent directly by the user when instantiating a decorator that can be used in classes that tells which methods of that class can be overridden to run with the decorator
It is an ``empty list`` by default.


``disallowed_methods``
-------------------------
This property is sent directly by the user when instantiating a decorator that can be used in classes that tells which methods of that class cannot be overridden to be executed with the decorator
It is an empty list by default and is changed when the Base decorator overwrites functions.
Here are the functions that are included in this property:

    * __class__
    * __delattr__
    * __dict__
    * __dir__
    * __doc__
    * __eq__
    * __format__
    * __ge__
    * __getattribute__
    * __gt__
    * __hash__
    * __init__
    * __init_subclass__
    * __le__
    * __lt__
    * __module__
    * __ne__
    * __new__
    * __reduce__
    * __reduce_ex__
    * __repr__
    * __setattr__
    * __sizeof__
    * __str__
    * __subclasshook__
    * __weakref__

If you want some to be overwritten, add them to the ``allowed_methods`` property


``class_injection``
-------------------------
This property is sent through the child decorator to say whether it can be placed under a class, thus injecting a radar function that overrides the other functions of that class so that we can trigger the decorator in each of them.
This property is ``True`` by default.


``instance``
-------------------------
This property is only for controlling the actions of each decorator.


``_traced_methods``
-------------------------
This property helps the Base decorator in injecting the radar function.


``is_class``
-------------------------
This property is changed when the Base decorator analyzes the object to be updated and allows the injection of the radar function to happen automatically


CheckTypes
===============
The CheckTypes decorator helps the developer to make sure that the variables passed to the function conform to the required types.
This decorator only works on functions, when instantiated under a class it will return an error saying that it supports functions and that it can be instantiated in static functions inside the class

Usage
-------------------------

.. code-block:: python

    from decmore import CheckTypes

    @CheckTypes()
    def func(var1: str, var2: list, var3: list | tuple):
        ...


    class klass:
        def __init__(self):
            ...

        @CheckTypes()
        @staticmethod
        def static(var1: list | tuple):
            ...


Profiler
===============
The Profiler decorator helps the developer to analyze the performance of his code by showing on the console, in order of time, which functions and lines took longer to execute.
Accepts to be instantiated in classes and can receive the ``allowed_methods`` and ``disallowed_methods`` attributes.

.. code-block:: python

    from time import sleep
    from decmore import Profiler


    @Profiler()
    def func():
        sleep(10)


    @Profiler(allowed_methods=['__init__'], disallowed_methods=['post'])
    class klass:
        def __init__(self):
            sleep(1)

        def get(self):
            ...

        def post(self):
            ...
