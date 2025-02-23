import multiprocessing
import pickle
import secrets
import time
from concurrent.futures import Future, ProcessPoolExecutor, ThreadPoolExecutor
from threading import Event

import pytest

from duty.database.json_file import JsonFile


def idprint(*args, **kwargs):
    import os
    import threading
    args = [str(v) for v in [f'p{os.getpid()}', f'{threading.get_native_id():3d}t', *args]]
    line = ' '.join(args) + '\n'
    print(line, end='')


def audithook(name, args):
    if name in ('compile', 'import'):
        return
    if name.startswith('object.__getattr__'):
        return
    if name == 'fcntl.flock':
        from fcntl import LOCK_EX, LOCK_SH, LOCK_UN
        operation = {
            LOCK_EX: 'Acquire exclusive lock',
            LOCK_SH: 'Acquire shared lock',
            LOCK_UN: 'Release lock'
        }.get(args[1], args[1])
        args = (args[0], operation)
    idprint(name, args)


@pytest.fixture
def json_file(local_dir):
    file = JsonFile(local_dir / 'pivo.json', local_dir / 'pivo.lock')
    yield file
    file.close()


def wait_event_once(ev: Event, timeout=None):
    res = ev.wait(timeout=timeout)
    if res:
        ev.clear()
    return res


def run_test_locking_thread1(event1, event2, json_file: JsonFile):
    with json_file.write_context as ctx:
        ctx.write(0)
        event2.set()
        assert not wait_event_once(event1, 1), 'Unexpected read from other thread'


def run_test_locking_thread2(event1, event2, json_file: JsonFile):
    wait_event_once(event2)
    assert json_file.read() == 0
    event1.set()


def run_test_locking_deadlock(json_file: JsonFile, event):
    with json_file.write_context:
        event.set()
        json_file.read()


def run_writes(file: JsonFile, writers: int, repeats: int):
    def do_some_writes():
        for _ in range(repeats):
            with file.write_context as ctx:
                value = ctx.read()
                ctx.write(value + 1)

    futures = []
    executor = ThreadPoolExecutor(max_workers=writers)
    for _ in range(writers):
        fut = executor.submit(do_some_writes)
        futures.append(fut)

    while any([not f.done() for f in futures]):
        file.read()

    for fut in futures:
        fut.result()


def run_concurrent_writing(data_file, lock_file):
    WRITERS = 10
    REPEATS = 100

    json_file = JsonFile(data_file, lock_file)

    with json_file.write_context as ctx:
        ctx.write(0)
    assert json_file.read() == 0

    futures: 'list[Future]' = []
    executor = ProcessPoolExecutor(
        max_workers=WRITERS,
        mp_context=multiprocessing.get_context('spawn')
    )
    for _ in range(WRITERS):
        fut = executor.submit(run_writes, json_file, WRITERS, REPEATS)
        futures.append(fut)

    while any([not f.done() for f in futures]):
        json_file.read()

    for fut in futures:
        fut.result()
    executor.shutdown()

    expected_result = WRITERS * WRITERS * REPEATS
    return json_file, expected_result


def test_basic(json_file: JsonFile):
    sample_value = secrets.token_hex()

    with pytest.raises(FileNotFoundError):
        json_file.read()

    with json_file.write_context as ctx:
        ctx.write(sample_value)
        assert ctx.read() == sample_value

    assert json_file.read() == sample_value


def test_locking_deadlock(json_file: JsonFile):
    mp_ctx = multiprocessing.get_context('spawn')
    event = mp_ctx.Event()
    process = mp_ctx.Process(
        target=run_test_locking_deadlock,
        args=(json_file, event)
    )
    process.start()
    time.sleep(1)
    assert process.is_alive() and event.is_set()
    process.kill()
    process.join()


def test_locking_inprocess(json_file: JsonFile):
    event1 = Event()
    event2 = Event()
    executor = ThreadPoolExecutor(max_workers=2)
    fut1 = executor.submit(run_test_locking_thread1, event1, event2, json_file)
    fut2 = executor.submit(run_test_locking_thread2, event1, event2, json_file)
    fut1.result()
    fut2.result()


def test_locking_interprocess(json_file: JsonFile):
    mp_ctx = multiprocessing.get_context('spawn')
    manager = mp_ctx.Manager()
    event1 = manager.Event()
    event2 = manager.Event()
    executor = ProcessPoolExecutor(max_workers=2, mp_context=mp_ctx)
    fut1 = executor.submit(run_test_locking_thread1, event1, event2, json_file)
    fut2 = executor.submit(run_test_locking_thread2, event1, event2, json_file)
    fut1.result()
    fut2.result()


def test_pickling(json_file: JsonFile):
    sample_value = secrets.token_hex()
    src_json_file = json_file
    with src_json_file.write_context as ctx:
        ctx.write(sample_value)
    assert getattr(src_json_file, '_lock_fd', None)

    dump = pickle.dumps(src_json_file)
    ldd_json_file: JsonFile = pickle.loads(dump)
    assert getattr(ldd_json_file, '_lock_fd', None) is None

    assert ldd_json_file.read() == sample_value


def test_concurrent_writing(local_dir):
    json_file, expected_result = run_concurrent_writing(
        local_dir / 'pivo.json',
        local_dir / 'pivo.lock',
    )

    assert json_file.read() == expected_result

    json_file.close()


def test_concurrent_writing_with_bad_lock(local_dir):
    # this should fail in term of data consistency
    # (cause after every write lock will change),
    # but all writes and reads should succeed

    json_file, expected_result = run_concurrent_writing(
        local_dir / 'pivo.json',
        local_dir / 'pivo.json'
    )

    assert json_file.read() < expected_result

    json_file.close()
