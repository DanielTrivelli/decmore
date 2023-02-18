from __future__ import annotations

from abc import ABC
from inspect import signature
from typing import Any, Callable
from re import match
from .default import BaseDecorator


def _check_function_names(func1: str, func2: str) -> bool:
    func1 = func1.split(' at ')[0].replace("<function ", '')
    func2 = func2.split(' at ')[0].replace("<function ", '')
    return func1 == func2


def function_match(value: str):
    return match(r'\s?<(function) | at \w*>', value)


class CheckTypes(BaseDecorator, ABC):
    def __init__(self):
        self.class_injection = False
        super(CheckTypes, self).__init__()

    def multiple_types(self, param_type: Any, param_value: Any, key: Any) -> str:
        error_string = ""
        param_type = [self.custom_eval(x) for x in param_type.split("|")]
        results = []
        for item in param_type:
            instance, param_str = item
            if function_match(param_str) and function_match(str(param_value)):
                same_function_name = _check_function_names(param_str, str(param_value))
                results.append(same_function_name)
            elif function_match(param_str):
                results.append(type(param_str) == type(param_value))
            else:
                results.append(isinstance(param_value, instance))

        if True not in filter(lambda result: result, results):
            param_type = [x[1] for x in param_type]
            expected = " or ".join(param_type)
            got = param_value if function_match(str(param_value)) else type(param_value)
            error_string += (
                f"\nParam '{key}' Expected {expected}, got {got} instead."
            )

        return error_string

    def error_constructor(
            self, args: list, kwargs: dict, idx: int, args_len: int, key: str, typ: str
    ) -> str:
        error_string = ""
        param_value = None
        if key != "" and ":" in typ:
            param_type = typ.split(":")[1]
            if key in kwargs:
                param_value = kwargs[key]
            elif idx <= args_len and args_len >= 0:
                param_value = args[idx]

            if "|" in param_type:
                error_string = self.multiple_types(param_type, param_value, key)
            elif not match(r'Any', param_type):
                param_type, param_type_str = self.custom_eval(param_type)
                if function_match(param_type_str):
                    param_value_str = str(param_value)
                    same_function_name = _check_function_names(param_type_str, param_value_str)
                    if param_type != param_value and not same_function_name and function_match(param_value_str):
                        error_string = f"\nParam '{key}' Expected {param_type}, got {param_value} instead."
                    elif param_type != param_value and not same_function_name and not function_match(param_value):
                        error_string = f"\nParam '{key}' Expected {param_type}, got {type(param_value)} instead."
                elif not isinstance(param_value, param_type):
                    error_string = f"\nParam '{key}' Expected {param_type}, got {type(param_value)} instead."
        return error_string

    def wrapper(self, *args: Any, **kwargs: Any) -> TypeError | Callable:
        error_string = ""
        params = [param for param in signature(self.instance).parameters.items() if param[0] != "self"]
        args_len = len(args) - 2
        args = list(args)
        args.pop(0)
        for idx, item in enumerate(params):
            key, t = item
            typ = t.__str__().replace("'", "")
            error_string += self.error_constructor(
                args, kwargs, idx, args_len, key, typ
            )

        if error_string != "":
            raise TypeError(error_string)
        return self.instance(*args, **kwargs)
