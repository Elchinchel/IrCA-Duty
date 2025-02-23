import threading
from typing import ContextManager


class ReadContext(ContextManager):
    def __init__(self, rwlock: 'RWLock', lock_cb, unlock_cb) -> None:
        self._rwlock = rwlock
        self._lock_cb = lock_cb
        self._unlock_cb = unlock_cb

    def __enter__(self):
        self._rwlock.read_acquire(self._lock_cb)

    def __exit__(self, exc_type, exc_value, traceback) -> bool | None:
        self._rwlock.read_release(self._unlock_cb)


class WriteContext(ReadContext):
    def __enter__(self):
        self._rwlock.write_acquire(self._lock_cb)

    def __exit__(self, exc_type, exc_value, traceback) -> bool | None:
        self._rwlock.write_release(self._unlock_cb)


class RWLock:
    def __init__(self) -> None:
        self._r_count = 0
        self._semaphore = threading.BoundedSemaphore(value=1)  # semaphore instead of lock for FIFO waiter priority
        self._write_lock = threading.Lock()
        self._r_count_lock = threading.Lock()

    def read_acquire(self, lock_cb=None):
        with self._semaphore:
            with self._r_count_lock:
                self._r_count += 1
                if self._r_count == 1:
                    self._write_lock.acquire()
                    if lock_cb is not None:
                        lock_cb()

    def read_release(self, unlock_cb=None):
        with self._r_count_lock:
            self._r_count -= 1
            if self._r_count == 0:
                self._write_lock.release()
                if unlock_cb is not None:
                    unlock_cb()

    def write_acquire(self, lock_cb=None):
        with self._semaphore:
            self._write_lock.acquire()
            if lock_cb is not None:
                lock_cb()

    def write_release(self, unlock_cb=None):
        self._write_lock.release()
        if unlock_cb is not None:
            unlock_cb()

    def read_ctx(self, lock_cb=None, unlock_cb=None):
        return ReadContext(self, lock_cb, unlock_cb)

    def write_ctx(self, lock_cb=None, unlock_cb=None):
        return WriteContext(self, lock_cb, unlock_cb)
