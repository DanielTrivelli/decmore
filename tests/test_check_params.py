from __future__ import annotations

import unittest
from src.decmore import CheckTypes
from threading import Thread


def func_test():
    return "Hello"


def func_test_2(): ...


class CheckTypesTestCase(unittest.TestCase):
    def test_without_params(self):
        @CheckTypes()
        def without_params():
            return 10 * 2

        self.assertEqual(without_params(), 20)

    def test_params(self):
        @CheckTypes()
        def params(num1: int, num2: float):
            return num1 - num2

        result = params(10, 2.1)
        self.assertEqual(result, 7.9)
        with self.assertRaises(TypeError):
            params(10.0, 2.1)

    def test_kwargs(self):
        @CheckTypes()
        def with_kwargs(num1: int, num2: float):
            return num1 - num2

        kwargs = {"num1": 20, "num2": 7.1}
        result = with_kwargs(**kwargs)
        self.assertEqual(result, 12.9)
        with self.assertRaises(TypeError):
            with_kwargs(**{"num1": 20, "num2": Thread})

    def test_multi_types(self):
        @CheckTypes()
        def multi_types(num1: int | float, num2: float):
            return num1 - num2

        kwargs1 = {"num1": 20, "num2": 7.1}
        result1 = multi_types(**kwargs1)
        self.assertEqual(result1, 12.9)

        kwargs2 = {"num1": 20.1, "num2": 7.1}
        result2 = multi_types(**kwargs2)
        self.assertAlmostEqual(result2, 13.0)
        with self.assertRaises(TypeError):
            multi_types(**{"num1": True, "num2": Thread})

    def test_with_function_param(self):
        @CheckTypes()
        def func_param(func: func_test):
            return func()

        result = func_param(func_test)
        self.assertEqual(result, "Hello")
        with self.assertRaises(TypeError):
            func_param(lambda x: 'error')

    def test_with_multi_function_param(self):
        @CheckTypes()
        def func_param(func: func_test | func_test_2):
            return func()

        result = func_param(func_test)
        self.assertTrue(isinstance(result, str))
        with self.assertRaises(TypeError):
            func_param(1)

    def test_with_error_function(self):
        @CheckTypes()
        def func_param(func: func_test): ...

        with self.assertRaises(TypeError):
            func_param(func_test_2)

        with self.assertRaises(TypeError):
            func_param('func_test_2')


if __name__ == '__main__':
    unittest.main()  # pragma: no cover
