from __future__ import annotations

from typing import Any, Callable
from abc import abstractmethod
from functools import partial
from inspect import getsource, isclass
from re import sub


class BaseDecorator(object):
    allowed_params = []
    allowed_methods = []
    disallowed_methods = []
    class_injection = True
    instance: Callable | None = None
    _traced_methods = {}
    _imports = ''
    _unsupported_counter = 0
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
            if (is_method and allowed) or attribute in self.allowed_methods or attribute == '__init__':
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
        return self.instance if self.is_class else self.overload_wrapper()

    def custom_eval(self, param_str: str):
        try:
            param_str = param_str.removeprefix(' ')
            if self._imports:
                exec(self._imports)
                self._imports = ''
            param_type = eval(param_str)
            self._unsupported_counter = 0
            return param_type, str(param_type)
        except (NameError, AttributeError) as error:
            self._unsupported_counter += 1
            if self._unsupported_counter > 1:
                raise NotImplementedError(
                    f"Type '{param_str.replace(' ', '').replace('~', '')}' has not been implemented"
                    f" or isn't working properly.\n"
                    f"Please open an issue in: https://github.com/DanielTrivelli/decmore/issues"
                )
            instance_file = self.instance.__globals__['__file__']
            error_string = str(error)
            if '__main__' not in error_string:
                package_name = sub(r'NameError: | is not defined', '', error_string.split("'")[1])
                param_object = param_str.split('.')[-1]
                import_list = []
                file = open(instance_file, 'r')
                for line in file.readlines():
                    if 'import' in line and package_name in line and param_object in line:
                        import_list.append(line)
                file.close()
                imports = ''.join(import_list)
                if imports:
                    module = imports.split(' ')[1].replace('\n', '')
                    if module not in param_str:
                        param_str = f"{module}.{param_str}"

                    if 'from' in imports:
                        imports = sub(r'\s?import(\s\w*,?)*', '', imports).replace('from', 'import')

                    self._imports = imports
                else:
                    root, module = instance_file.split('\\')[-2:]
                    module = module.replace('.py', '')
                    param_str = f'{root}.{module}.{param_str}'
                    self._imports = f'import {root}.{module}'
                return self.custom_eval(param_str)

    @abstractmethod
    def wrapper(self, inject=None, *args: Any, **kwargs: Any) -> Callable: ...

    @abstractmethod
    def __call__(self, instance: Callable) -> None | overload_wrapper | update_instance:
        return self.update_instance(instance)
