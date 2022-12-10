from __future__ import annotations

from abc import abstractmethod
from functools import partial
from inspect import getsource, isclass, getmembers
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

    def overload_wrapper(self, inject=None, *args, **kwargs):
        return partial(self.wrapper, inject, *args, **kwargs)

    def base_radar(self, _method, *args, **kwargs):
        method, source_code = self._traced_methods[_method].values()

        @self.overload_wrapper
        def radar(self, *args, **kwargs):
            if '*args' in source_code and '**kwargs' not in source_code:
                return method(self, *args)
            elif '*args' not in source_code and '**kwargs' in source_code:
                return method(self, **kwargs)
            return method(self, *args, **kwargs)

        return partial(radar, self.instance, *args, **kwargs)

    def __injection(self) -> None:
        instance_methods = []
        for attribute in dir(self.instance):
            is_method = callable(getattr(self.instance, attribute))
            allowed = attribute not in self.disallowed_methods and not attribute.startswith('__')
            if (is_method and allowed) or attribute in self.allowed_methods:
                instance_methods.append(attribute)

        for method in instance_methods:
            code_str = f'self.instance.{method}'
            this_method = eval(code_str)
            self._traced_methods[method] = {
                "method": this_method,
                "code": getsource(this_method)
            }
            code_str += f' = self.base_radar("{method}")'
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
