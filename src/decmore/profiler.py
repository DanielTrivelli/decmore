from cProfile import Profile
from io import StringIO
from pstats import Stats
from typing import Any, Callable


class Profiler(object):
    def __init__(self) -> None:
        self.instance = None

    def wrapper(self, *args: Any, **kwargs: Any) -> Any:
        pr = Profile()
        pr.enable()
        retval = self.instance(*args, **kwargs)
        pr.disable()
        s = StringIO()
        ps = Stats(pr, stream=s).sort_stats("time")
        ps.print_stats()
        print(s.getvalue())
        return retval

    def __call__(self, instance: Callable) -> wrapper:
        if not self.instance:
            self.instance = instance
        return self.wrapper
