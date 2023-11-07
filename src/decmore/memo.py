from __future__ import annotations

from abc import ABC
from typing import (
    Any,
    Callable
)
from decmore.default import BaseDecorator


class Cache(BaseDecorator, ABC):
    def __init__(self):
        self.cache = {}
        self.class_injection = False
        super(Cache, self).__init__()

    def wrapper(self, *args: Any, **kwargs: Any) -> Callable:
        func = self.instance
        key = self._create_id(args=args, kwargs=kwargs, random_idx=False)
        cached = self.cache.get(key)
        if not cached:
            response = func(*args, **kwargs)
            self.cache[key] = response
            return response
        return cached

