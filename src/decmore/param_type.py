from __future__ import annotations

from abc import ABC
from inspect import signature
from typing import Any, Callable

from decmore.default import BaseDecorator


class CheckTypes(BaseDecorator, ABC):
    def __init__(self):
        self.class_injection = False
        super(CheckTypes, self).__init__()

    @staticmethod
    def multiple_types(param_type: Any, param_value: Any, key: Any) -> str:
        error_string = ""
        param_type = [eval(x) for x in param_type.split("|")]
        param_value_type = type(param_value)
        if param_value_type not in param_type:
            param_type = [str(x) for x in param_type]
            expected = " or ".join(param_type)
            error_string += (
                f"\nParam '{key}' Expected {expected}, got {type(param_value)} instead."
            )
        return error_string

    def error_constructor(
            self, args: tuple, kwargs: dict, idx: int, args_len: int, key: str, typ: str
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
            elif param_type not in ["Any", "any"]:
                param_type = eval(param_type)
                if not isinstance(param_value, param_type):
                    error_string = f"\nParam '{key}' Expected {param_type}, got {type(param_value)} instead."

        return error_string

    def wrapper(self, *args: Any, **kwargs: Any) -> TypeError | Callable:
        error_string = ""
        params = [param for param in signature(self.instance).parameters.items() if param[0] != "self"]
        args_len = len(args) - 1
        for idx, item in enumerate(params):
            key, t = item
            typ = t.__str__()
            error_string += self.error_constructor(
                args, kwargs, idx, args_len, key, typ
            )

        if error_string != "":
            raise TypeError(error_string)
        return self.instance(*args, **kwargs)


