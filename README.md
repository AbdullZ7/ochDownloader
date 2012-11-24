This is a lame attempt to bring coroutines into ochDownloader.

There are two main issues:

First, the Qt loop with gevent integration sucks:

    while True:
        while app.hasPendingEvents():
            app.processEvents()
            gevent.sleep(0.01)
        gevent.sleep(0.1)

I have no idea how to fix this, yet.


Second, the idle_queue_dispatcher is not safe, since you cant use gevent.Queue from a child thread.
The patch_all() does not allow QThreads to run, so you cant patch threads.
Solution: use gevent.spawn to create the coroutine and use gevent.Queue + signals to wait/block and emit them.

Note: The main loop never exits, so the process must be terminated.


Dependencies:
Python 2.7.3
PySide 1.1.2
Gevent 1.0rc1 (and whatever it depends on)


____________________________________________________________________________


Copyright (C) 2012 Esteban Borsani ochdownloader@gmail.com

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation; either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.