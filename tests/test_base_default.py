from __future__ import annotations

import unittest
from src.decmore.default import BaseDecorator
from src.decmore import CheckTypes
from abc import ABC
from typing import AnyStr
from aux_functions import aux_function


class InjectionFalseDecorator(BaseDecorator, ABC):
    def __init__(self):
        self.class_injection = False
        super(InjectionFalseDecorator, self).__init__()

    def wrapper(self, inject=None, *args: Any, **kwargs: Any) -> Callable:
        return self.instance(*args, **kwargs)  # pragma: no cover


class InjectionTrueDecorator(BaseDecorator, ABC):
    def __init__(self):
        super(InjectionTrueDecorator, self).__init__()

    def wrapper(self, inject=None, *args: Any, **kwargs: Any) -> Callable:
        func = self.instance if not inject else inject
        if args or kwargs:
            ret = func(*args, **kwargs)
        else:
            ret = func()  # pragma: no cover
        return ret


@InjectionTrueDecorator()
class FormatRadar:
    def __init__(self):
        self.args = None
        self.kwargs = None

    def get(self, *args):
        self.args = args
        return self.args

    def post(self, **kwargs):
        self.kwargs = kwargs
        return self.kwargs


def test_func(): ...


class BaseDecoratorTestCase(unittest.TestCase):
    def test_param_filter(self):
        base = BaseDecorator
        base.allowed_params = ['param_1']
        base_withou_error = base(param_1=1)
        self.assertEqual(base_withou_error.params, {'param_1': 1})
        with self.assertRaises(AttributeError):
            base.allowed_params = []
            base_error = base(param_1=1)

    def test_injection_not_supported(self):
        class_str = """@InjectionFalseDecorator()\nclass NewClass:..."""
        with self.assertRaises(TypeError):
            exec(compile(class_str, 'NewClass', 'exec'))

    def test_format_radar(self):
        f_radar = FormatRadar()
        get_args = (1, 2, 3)
        post_kwargs = {'a': 1, 'b': 2, 'c': 3}
        self.assertEqual(f_radar.get(*get_args), get_args)
        self.assertEqual(f_radar.post(**post_kwargs), post_kwargs)

    def test_not_implemented_custom_eval(self):
        @CheckTypes()
        def not_implemented(f: teste): ...

        with self.assertRaises(NotImplementedError):
            not_implemented(test_func)

    def test_with_module(self):
        @CheckTypes()
        def not_implemented(f: AnyStr): ...

        with self.assertRaises(TypeError):
            not_implemented(test_func)





if __name__ == '__main__':
    unittest.main()  # pragma: no cover
