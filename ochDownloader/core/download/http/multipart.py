import logging
import threading
from queue import Queue

from .worker import worker, is_chunk_complete, DATA_BUFSIZ
from core.config import conf
from core.utils.concurrent.thread import Future
from core.utils.queue import PersistentQueue

logger = logging.getLogger(__name__)

START, END = range(2)


def spawn(i, chunks, queue, w_queue, e_queue, err_event, stop_event):
    return Future(target=worker, args=(i, chunks, queue, w_queue, e_queue, err_event, stop_event))


def create_chunks(size):
    max_conn = conf.get_max_conn()
    chunk_size = (size / max_conn)
    chunk_size = (chunk_size / DATA_BUFSIZ) * DATA_BUFSIZ

    if not chunk_size:  # too small
        return [(0, size), ]

    chunks = []
    start = 0

    for _ in range(max_conn):
        end = start + chunk_size
        chunks.append((start, end))
        start += chunk_size

    chunks[-1] = (chunks[-1][START], size)

    return chunks


def get_chunks_size_complete(chunks):
    complete = 0
    previous_chunk_end = 0

    for chunk in chunks:
        complete += chunk[START] - previous_chunk_end
        previous_chunk_end = chunk[END]

    return complete


def pooler(di, fh):
    if not di.chunks:
        di.chunks = create_chunks(di.size)
    else:  # resume
        di.size_complete = get_chunks_size_complete(di.chunks)
        di.size_tmp = di.size_complete

    logger.debug("{} connections: {}".format(len(di._chunks), di._chunks))

    queue = Queue(len(di.chunks) + 1)
    w_queue = Queue(1)
    w_queue.put(tuple())
    e_queue = PersistentQueue(item=None)
    err_event = threading.Event()

    threads = [spawn(i, tuple(di.chunks), queue, w_queue, e_queue, err_event, di.stop_event)
               for i, chunk in enumerate(di.chunks)
               if not chunk[END] or chunk[START] < chunk[END]]  # end may be 0

    th_count = len(threads)

    while th_count:
        item = queue.get()

        if item is None:
            th_count -= 1
            continue

        i, chunk, data, len_data = item

        try:
            fh.seek(chunk[START] - len_data)
            fh.write(data)
        except OSError as err:
            logger.exception(err)
            err_event.set()
            di.message = str(err)
            break

        di.chunks[i] = (chunk[START], di.chunks[i][END])
        di.update()

    for th in threads:
        th.result(wait=True)

    #if err_event.is_set():
        #raise Exception()

    if not (di.is_stopped() or are_chunks_complete(di.chunks)):
        err_event.set()
        di.message = "Incomplete chunk"


def are_chunks_complete(chunks):
    for chunk in chunks:
        if not is_chunk_complete(chunk):
            logger.debug("Incomplete: {} of {}".format(chunk[START], chunk[END]))
            return False

    return True