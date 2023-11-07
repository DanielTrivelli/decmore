from abc import ABC
from cProfile import Profile
from io import StringIO
from pstats import Stats
from typing import (
    Callable,
    Any
)
from decmore.default import BaseDecorator


class Profiler(BaseDecorator, ABC):
    def __init__(self, allowed_methods: list = None, disallowed_methods: list = None):
        if allowed_methods:
            self.allowed_methods = allowed_methods
        if disallowed_methods:
            self.disallowed_methods = disallowed_methods
        super(Profiler, self).__init__()

    def wrapper(self, *args: Any, **kwargs: Any) -> Callable:
        if self.is_class:
            key = f'{self._instance_id}_inject'
            func = kwargs[key]
            del kwargs[key]
        else:
            func = self.instance
        pr = Profile()
        pr.enable()
        if args or kwargs:
            retval = func(*args, **kwargs)
        else:
            retval = func()
        pr.disable()
        s = StringIO()
        ps = Stats(pr, stream=s).sort_stats("time")
        ps.print_stats()
        print(s.getvalue())
        return retval
