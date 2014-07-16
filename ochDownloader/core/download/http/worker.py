import logging
import time
from contextlib import closing

from .exceptions import IncompleteChunk
from core.utils.http.rate_limit import TokenBucket
from core.utils.http import request

logger = logging.getLogger(__name__)
bucket = TokenBucket()

DATA_BUFSIZ = 8 * 1024  # 8K.
START, END = range(2)


def take_next_chunk(next_chunk_i, chunk, chunks, w_queue):
    # check if next chunk can be resumed
    try:
        if chunk[END] != chunks[next_chunk_i][START]:
            return False
    except IndexError:
        # no more chunks left
        return False

    if not take_chunk(next_chunk_i, w_queue):
        return False

    return True


def is_chunk_complete(chunk):
    if chunk[START] < chunk[END]:
        return False
    else:
        return True


def take_chunk(i, w_queue):
    # check if we can download
    thread_ids = w_queue.get()

    try:
        if i not in thread_ids:
            thread_ids += tuple(i)
            return True
        else:
            return False
    finally:
        w_queue.put(thread_ids, block=False)


def rate_limit(len_data):
    if bucket.rate:
        seconds = bucket.consume(len_data)
        if seconds:  # avoid thread switching if seconds == 0
            time.sleep(seconds)


def get_source():
    return


def worker(i, chunks, queue, w_queue, e_queue, err_event, stop_event):
    """
    @i: thread number
    @chunks: chunks tuple
    @_queue: file writting
    @w_queue: control threads start up
    @e_queue: error message
    @err_event: stop all threads, setted on thread error
    @stop_event: stop all threads, setted from main thread
    """
    try:
        with closing(get_source()) as s:
            if not take_chunk(i, w_queue):
                return

            while True:
                data = s.read(DATA_BUFSIZ)
                len_data = len(data)
                chunk = (chunks[i][START] + len_data, chunks[i][END])
                queue.put((i, chunk, data, len_data))

                if not len_data or (chunk[END] and chunk[START] == chunk[END]):
                    if not is_chunk_complete(chunk):
                        raise IncompleteChunk("Incomplete chunk")

                    if not take_next_chunk(i + 1, chunk, chunks, w_queue):
                        return

                    i += 1

                rate_limit(len_data)

                if err_event.is_set() or stop_event.is_set():
                    return

    except (IncompleteChunk, request.RequestError) as err:
        logger.exception(err)
        err_event.set()
        #e_queue.put(str(err))
    finally:
        queue.put(None)