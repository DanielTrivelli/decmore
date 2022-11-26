from __future__ import annotations

from abc import abstractmethod
from functools import partial
from inspect import getsource, isclass
from re import sub
from typing import Any, Callable


class BaseDecorator(object):
    allowed_params = []
    allowed_methods = []
    disallowed_methods = []
    class_injection = True
    instance: Callable | None = None
    _traced_methods = {}
    is_class = False

    def __init__(self, **kwargs: Any) -> None:
        self.params: dict | None = kwargs
        if kwargs:
            self.__filter_params()

    def overload_wrapper(self, inject, *args, **kwargs):
        return partial(self.wrapper, inject, *args, **kwargs)

    def __injection(self) -> None:
        default_disallowed = ['__class__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__', '__format__',
                              '__ge__', '__getattribute__', '__gt__', '__hash__', '__init__', '__init_subclass__',
                              '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__',
                              '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__']

        default_disallowed.extend(self.disallowed_methods)
        default_disallowed = [x for x in default_disallowed if x not in self.allowed_methods]
        instance_methods = [x for x in dir(self.instance) if x not in default_disallowed]

        overload_wrapper = self.overload_wrapper

        base_radar_str = """@overload_wrapper\ndef base_radar(self=self, *args, **kwargs):
        return self._traced_methods["{}"](self, *args, **kwargs)
        """
        for method in instance_methods:
            code_str = f'self.instance.{method}'
            this_method = eval(code_str)
            self.params['inject'] = this_method
            self._traced_methods[method] = this_method
            _base = base_radar_str.format(method)
            if '@staticmethod' in getsource(this_method):
                _base = sub(r']\((self,\s)', '](', _base)
            code_str += ' = base_radar'
            exec(compile(_base, 'base_radar', 'exec'))
            exec(compile(code_str, method, 'exec'))

    def __filter_params(self) -> None:
        if not self.allowed_params:
            raise AttributeError
        self.params = {k: v for k, v in self.params.items() if k in self.allowed_params}

    def update_instance(self, instance: Callable) -> TypeError | instance | wrapper:
        if not self.instance:
            self.instance = instance
            self.is_class = isclass(instance)
            if self.is_class:
                if self.class_injection:
                    self.__injection()
                else:
                    raise TypeError(
                        f"{self.__class__.__name__} decorator cannot be called in classes, "
                        f"try calling it in functions inside the desired class. "
                        f"Works only on static methods"
                    )
        return self.instance if self.is_class else self.wrapper

    @abstractmethod
    def wrapper(self, inject=None, *args: Any, **kwargs: Any) -> Callable:
        ...

    @abstractmethod
    def __call__(self, instance: Callable) -> None | wrapper | update_instance:
        return self.update_instance(instance)
