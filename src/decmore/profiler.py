from abc import ABC
from cProfile import Profile
from io import StringIO
from pstats import Stats
from typing import Callable, Any
from decmore.default import BaseDecorator


class Profiler(BaseDecorator, ABC):
    def __init__(self, allowed_methods: list = None, disallowed_methods: list = None):
        if allowed_methods:
            self.allowed_methods = allowed_methods
        if disallowed_methods:
            self.disallowed_methods = disallowed_methods
        super(Profiler, self).__init__()

    def wrapper(self, inject: Callable = None, *args: Any, **kwargs: Any) -> Callable:
        func = self.instance if not inject else inject
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
