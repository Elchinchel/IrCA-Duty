import json
import os
from contextlib import AbstractContextManager
from fcntl import LOCK_EX, LOCK_SH, LOCK_UN, flock
from pathlib import Path
from tempfile import NamedTemporaryFile
from threading import Lock
from typing import Any

from duty.utils.rwlock import RWLock


class WriteContext(AbstractContextManager):
    """
    Instance of this object is not thread safe,
    only one method should be called at the same time
    """

    def __init__(self, json_file: 'JsonFile') -> None:
        self._json_file = json_file

    def read(self) -> Any:
        with open(self._json_file.name, encoding='utf-8') as file:
            return self._json_file._load(file)

    def write(self, data: Any):
        tmp_file = NamedTemporaryFile('w', encoding='utf-8', delete=False)
        try:
            self._json_file._dump(tmp_file, data)
            tmp_file.close()
            os.rename(tmp_file.name, self._json_file.name)
        except Exception:
            try:
                os.unlink(tmp_file.name)
            except FileNotFoundError:
                pass

    def __enter__(self):
        self._json_file._write_lock_ctx.__enter__()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._json_file._write_lock_ctx.__exit__(exc_type, exc_value, traceback)


class JsonFile:
    def __init__(self, name: Path, lockname: Path) -> None:
        self.name = name
        # separate lock file is required due to data file replacement
        self._lockname = lockname
        self._flock_mutex = Lock()

        rwlock = RWLock()
        self._read_lock_ctx = rwlock.read_ctx(
            lock_cb=lambda: self._call_flock(LOCK_SH),
            unlock_cb=lambda: self._call_flock(LOCK_UN)
        )
        self._write_lock_ctx = rwlock.write_ctx(
            lock_cb=lambda: self._call_flock(LOCK_EX),
            unlock_cb=lambda: self._call_flock(LOCK_UN)
        )

    def _load(self, file) -> Any:
        return json.load(file)

    def _dump(self, file, data: Any):
        json.dump(data, file, ensure_ascii=False, indent=4)

    def _call_flock(self, operation: int):
        try:
            fd = self._lock_fd
        except AttributeError:
            fd = os.open(self._lockname, os.O_CREAT)
            self._lock_fd = fd
        with self._flock_mutex:
            flock(fd, operation)

    def read(self):
        with self._read_lock_ctx:
            with open(self.name, encoding='utf-8') as file:
                return self._load(file)

    @property
    def write_context(self) -> WriteContext:
        """
        Context manager for writing. Example usage:
        ```
        with json_file.write_context as ctx:
            data = ctx.read()
            *modify data*
            ctx.write(data)
        ```
        While code inside the context, file wouldn't be modified by other
        processes or threads using same JsonFile.
        """
        return WriteContext(self)

    def close(self):
        """Close lock file"""
        try:
            fd = self._lock_fd
        except AttributeError:
            return
        os.close(fd)

    def __reduce__(self):
        return (JsonFile, (self.name, self._lockname))
