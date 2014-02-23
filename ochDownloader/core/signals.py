from .dispatch import Signal


download_complete = Signal()  # args: download_item

all_downloads_complete = Signal()

quit = Signal()

limit_exceeded = Signal()

add_raw_downloads = Signal()  # args: links, path, cookie