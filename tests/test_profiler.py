import unittest
from src.decmore import Profiler
from time import sleep
from subprocess import run
from os import remove, listdir
from re import search, findall
import platform

function_string = """
from time import sleep
from src.decmore import Profiler

@Profiler()
def second_function():
    sleep(1)

if __name__ == '__main__':
    second_function()

"""

class_string = """
from time import sleep
from src.decmore import Profiler

@Profiler()
class MyNewClass:
    def __init__(self):
        self.count = 0

    def method(self):
        self.count += 1
        sleep(1)
        return self.count
        
    def other_method(self):
        self.count += 2
        sleep(1)
        return self.count

if __name__ == '__main__':
    my_new_class = MyNewClass()
    my_new_class.method()
    my_new_class.other_method()

"""

os_name = platform.system()


class ProfilerTestCase(unittest.TestCase):

    def test_function_params(self):
        @Profiler()
        def first_function(*args, **kwargs):
            return args, kwargs

        self.assertEqual(first_function(1, 2, **{"a": 1, "b": 2}), ((1, 2), {'a': 1, 'b': 2}))

    def test_function_without_params(self):
        @Profiler()
        def other_function():
            return 10 * 2

        self.assertEqual(other_function(), 20)

    def test_function_output_logs(self):
        second_function_file = open('second_function.py', 'w')
        second_function_file.write(function_string)
        second_function_file.close()
        python_command = 'python' if os_name == 'Windows' else 'python3'
        out = run([python_command, 'second_function.py'], capture_output=True).stdout.decode('utf-8')
        remove('second_function.py')
        total_time = float(search(r'([0-9]*\s\bfunction calls in)(\s[0-9]\b.[0-9]*\s)(\bseconds)', out).groups()[1])
        self.assertTrue(1.0 <= total_time <= 1.2)

    def test_class_args(self):
        @Profiler()
        class MyClass:
            def __init__(self):
                self.count = 0

            def method(self, number):
                self.count += number
                sleep(1)
                return self.count / 2, number

        my_new_class = MyClass()
        result = my_new_class.method(10)
        self.assertEqual(result, (5, 10))

    def test_class_output_logs(self):
        klass_file = open('klass.py', 'w')
        klass_file.write(class_string)
        klass_file.close()
        python_command = 'python' if os_name == 'Windows' else 'python3'
        out = run([python_command, 'klass.py'], capture_output=True).stdout.decode('utf-8')
        remove('klass.py')
        times = (
            (0.0, 0.2),
            (1.0, 1.2),
            (1.0, 1.2)
        )
        total_time = findall(r'([0-9]*\s\bfunction calls in)(\s[0-9]\b.[0-9]*\s)(\bseconds)', out)
        for total, expected in zip(total_time, times):
            this_time = float(total[1])
            first, second = expected
            self.assertTrue(first <= this_time <= second)

    def test_allowed_and_disallowed_methods(self):
        @Profiler(allowed_methods=['get'], disallowed_methods=['update'])
        class klass:
            def __init__(self):
                self.number = 1

            def get(self):
                return self.number

            def update(self, new_number):
                self.number = new_number
                return self.number

        this_class = klass()

        self.assertEqual(this_class.get(), 1)
        self.assertEqual(this_class.update(24), 24)


if __name__ == '__main__':
    unittest.main()  # pragma: no cover
