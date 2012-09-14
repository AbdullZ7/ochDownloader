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

        self.timer = parent.idle_timeout(1000, self.update)

        self.exec_()

    def update(self):
        pass

    def reject(self):
        self.timer.stop()
        self.hide()
        return QDialog.Rejected


import threading
import importlib
import Queue

class Plugin(threading.Thread):
    def __init__(self, links_list):
        threading.Thread.__init__(self)
        self.video_queue = Queue.Queue()
        self.links_list = links_list

    def run(self):
        th_list = []
        for link in self.links_list:
            th = threading.Thread(group=None, target=self.parser, name=None, args=(link, ))
            th_list.append(th)
            th.start()
        for th in th_list:
            th.join()

    def parser(self, link):
        #from addons.video_grabber.plugins import unsupported

        host = misc.get_host(link)
        try:
            module = importlib.import_module("plugins.{0}".format(host))
            p = module.Download(link)
            p.parse()
        except ImportError as err:
            logger.debug(err)
        except Exception as err:
            logger.exception(err)
        else:
            for video in p.video_list:
                self.video_queue.put(video)
