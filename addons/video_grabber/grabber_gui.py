import logging
logger = logging.getLogger(__name__)

from core import misc

from PySide.QtGui import *
from PySide.QtCore import *


class GrabberDialog(QDialog):
    """"""
    def __init__(self, parent):
        """"""
        #TODO: change textEdit to "searching" text on OK, add links after finish.
        #or else show an error message.
        QDialog.__init__(self, parent, Qt.WindowSystemMenuHint | Qt.WindowTitleHint)
        self.setWindowTitle(_('Video Grabber'))
        self.resize(340, 200)

        self.parent = parent

        vbox = QVBoxLayout()
        vbox.setSpacing(20)
        self.setLayout(vbox)

        group_log = QGroupBox(_('Paste Your Links (one link per line):'))
        vbox_log = QVBoxLayout()
        group_log.setLayout(vbox_log)
        vbox.addWidget(group_log)

        self.text_view = QPlainTextEdit()

        vbox_log.addWidget(self.text_view)

        hbox = QHBoxLayout()
        hbox.addStretch(0)
        vbox.addLayout(hbox)

        btn_close = QPushButton(_('Cancel'))
        btn_close.clicked.connect(self.reject)
        btn_close.setFixedHeight(35)
        btn_close.setMaximumWidth(80)
        hbox.addWidget(btn_close)

        btn_ok = QPushButton(_('OK'))
        btn_ok.clicked.connect(self.on_ok)
        btn_ok.setDefault(True)
        btn_ok.setFixedHeight(35)
        btn_ok.setMaximumWidth(80)
        hbox.addWidget(btn_ok)

        self.exec_()

    def on_ok(self):
        links_list = misc.links_parser(self.text_view.toPlainText())
        self.hide()
        if links_list:
            w_dialog = WaitDialog(self.parent, links_list)
            video_links = w_dialog.video_links
            if video_links:
                #self.parent.links_checking(video_links)
                pass
        self.accept()


class WaitDialog(QDialog):
    """"""
    def __init__(self, parent, links_list):
        """"""
        QDialog.__init__(self, parent, Qt.WindowSystemMenuHint | Qt.WindowTitleHint)
        self.setWindowTitle(_('Video Grabber'))
        self.resize(340, 200)

        self.links_list = links_list
        self.video_links = []

        vbox = QVBoxLayout()
        vbox.setSpacing(20)
        self.setLayout(vbox)

        label_searching = QLabel(_('Searching...'))
        vbox.addWidget(label_searching)

        self.th_plugin = Plugin(links_list)
        self.th_plugin.start()
        self.timer = parent.idle_timeout(1000, self.update)

        self.exec_()

    def update(self):
        if not self.th_plugin.is_alive():
            self.accept()

    def accept(self):
        self.timer.stop()
        self.hide()
        return QDialog.Accepted

    def reject(self):
        self.timer.stop()
        self.hide()
        return QDialog.Rejected


import threading
import importlib
import Queue

class Plugin(threading.Thread):
    def __init__(self, links_list, pool_limit=10):
        threading.Thread.__init__(self)
        self.limiter_queue = Queue.Queue(pool_limit)
        self.video_queue = Queue.Queue()
        self.links_list = links_list

    def run(self):
        self.create_threads()

    def create_threads(self):
        th_list = [self.spawn_thread(link) for link in self.links_list]
        for th in th_list:
            th.join()

    def spawn_thread(self, link):
        self.limiter_queue.put(None) #block if limit is reached
        th = threading.Thread(group=None, target=self.worker_thread, name=None, args=(link, ))
        th.start()
        return th

    def worker_thread(self, link):
        try:
            self.parser(link)
        finally:
            self.limiter_queue.get_nowait() #we are done

    def parser(self, link):
        #from addons.video_grabber.plugins import unsupported

        host = misc.get_host(link)
        try:
            module = importlib.import_module("plugins.{0}".format(host))
            p = module.Grab(link)
            p.parse()
        except ImportError as err:
            logger.debug(err)
        except Exception as err:
            logger.exception(err)
        else:
            for video in p.video_list:
                self.video_queue.put(video)