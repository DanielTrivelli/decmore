from __future__ import annotations

from abc import ABC
from typing import Any
from itertools import chain
from threading import Thread
from hashlib import md5
from random import randint
from decmore.default import BaseDecorator
import numpy as np


class ToThreads(BaseDecorator, ABC):
    def __init__(self, amount: int, return_expected: bool = False):
        self.amount = amount
        self.return_expected = return_expected
        self.__threads = {}
        self.__active_threads = []
        self.__threads_response = []
        self.__threads_status = {}
        self.__instance_id = None
        self.class_injection = False
        super(ToThreads, self).__init__()

    def __delete_threads(self, target):
        if target == 'all':
            self.__threads = {}
            self.__threads_response = []
        else:
            self.__active_threads.remove(target)
            del self.__threads[target]
            del self.__threads_response[target]

    def __check_threads_status(self):
        for thread_key, thread in self.__threads.items():
            print(thread_key)

    def __thread(self, *args, **kwargs):
        thread_key = kwargs[self.__instance_id]
        del kwargs[self.__instance_id]
        response = self.instance(*args, **kwargs)
        if self.return_expected:
            self.__threads_response.append(response)
        try:
            self.__delete_threads(thread_key)
        except ValueError:
            pass

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
                    work_thread[idx]['args'].append(s)
            else:
                for i in range(self.amount):
                    work_thread[i]['args'].append(arg)
        for key, value in kwargs.items():
            if isinstance(value, list) or isinstance(value, tuple):
                sl = np.array_split(value, self.amount)
                for idx, s in enumerate(sl):
                    work_thread[idx]['kwargs'][key] = sl
            else:
                for i in range(self.amount):
                    work_thread[i]['kwargs'][key] = value
        return work_thread

    def __set_threads(self, *args, **kwargs) -> dict[str, Thread]:
        work = self.__divide_work_between_threads(*args, **kwargs)
        for t in range(self.amount):
            random_idx = randint(0, 1025)
            key = f"{self.__instance_id}-{random_idx}-{t}-{args}-{kwargs}".encode('utf-8')
            thread_key = md5(key).hexdigest()
            mod_args, mod_kwargs = work[t].values()
            mod_kwargs[self.__instance_id] = thread_key
            self.__threads[thread_key] = Thread(target=self.__thread, args=mod_args, kwargs=mod_kwargs)
        return self.__threads

    def __start_threads(self):
        for thread_key, thread in self.__threads.items():
            if thread_key not in self.__active_threads:
                thread.start()
                self.__active_threads.append(thread_key)

    def wrapper(self, *args, **kwargs) -> list[Any] | None:
        self.__instance_id = str(id(self.instance))
        self.__set_threads(*args, **kwargs)
        self.__check_threads_status()
        self.__start_threads()
        if self.return_expected:
            while len(self.__threads_response) < len(self.__threads):
                continue
            else:
                response = list(chain.from_iterable(self.__threads_response))
                self.__delete_threads('all')
                return response
