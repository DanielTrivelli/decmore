from __future__ import annotations

from abc import ABC
from typing import Any
from itertools import chain
from threading import Thread
from traceback import format_exc
from logging import error
import numpy as np
from decmore.default import BaseDecorator


class ToThreads(BaseDecorator, ABC):
    def __init__(self, amount: int, return_expected: bool = False):
        self.amount = amount
        self.return_expected = return_expected
        self.__threads = {}
        self.__active_threads = []
        self.__threads_response = []
        self.class_injection = False
        super(ToThreads, self).__init__()

    def __delete_threads(self, target):
        try:
            if target == 'all':
                self.__threads = {}
                self.__threads_response = []
                self.__active_threads = []
            else:
                self.__active_threads.remove(target)
                del self.__threads[target]
                del self.__threads_response[target]
        except ValueError:
            pass

    def __thread(self, *args, **kwargs):
        thread_key = kwargs[self._instance_id]
        del kwargs[self._instance_id]
        try:
            response = self.instance(*args, **kwargs)
            if self.return_expected:
                self.__threads_response.append(response)
                self.__delete_threads(thread_key)
        except Exception:
            error(f"There was an error executing the thread's target function.\n"
                  f"internal_thread_id: {thread_key}\nexception: {format_exc()}")
            self.__delete_threads(thread_key)
            if not self.__active_threads:
                exit()

    def __divide_work_between_threads(self, *args, **kwargs):
        work_thread = {}

        for i in range(self.amount):
            work_thread[i] = {
                'args': [],
                'kwargs': {}
            }
        for arg in args:
            if isinstance(arg, list) or isinstance(arg, tuple):
                sl = np.array_split(arg, self.amount)
                for idx, s in enumerate(sl):
                    work_thread[idx]['args'].append(s.tolist())
            else:
                for i in range(self.amount):
                    work_thread[i]['args'].append(arg)
        for key, value in kwargs.items():
            if isinstance(value, list) or isinstance(value, tuple):
                sl = np.array_split(value, self.amount)
                for idx, s in enumerate(sl):
                    work_thread[idx]['kwargs'][key] = s.tolist()
            else:
                for i in range(self.amount):
                    work_thread[i]['kwargs'][key] = value
        return work_thread

    def __set_threads(self, *args, **kwargs) -> dict[str, Thread]:
        work = self.__divide_work_between_threads(*args, **kwargs)
        for t in range(self.amount):
            thread_key = self._create_id(args, kwargs)
            mod_args, mod_kwargs = work[t].values()
            mod_kwargs[self._instance_id] = thread_key
            self.__threads[thread_key] = Thread(target=self.__thread, args=mod_args, kwargs=mod_kwargs)
        return self.__threads

    def __start_threads(self):
        for thread_key, thread in self.__threads.items():
            if thread_key not in self.__active_threads:
                thread.run()
                self.__active_threads.append(thread_key)

    def wrapper(self, *args, **kwargs) -> list[Any] | None:
        self.__set_threads(*args, **kwargs)
        self.__start_threads()
        if self.return_expected:
            while len(self.__threads_response) < len(self.__threads):
                continue
            else:
                response = list(chain(self.__threads_response))
                self.__delete_threads('all')
                return response
