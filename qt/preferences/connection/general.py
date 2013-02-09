from core.config import conf

from PySide.QtGui import *
from PySide.QtCore import *


class General(QGroupBox):
    def __init__(self, parent=None):
        QGroupBox.__init__(self, _('General:'))

        #vbox_general = QVBoxLayout()
        grid_general = QGridLayout()
        self.setLayout(grid_general)

        label_retries = QLabel(_('Retries limit:'))
        #label_retries.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.retries_box = QSpinBox()
        #self.retries_box.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.retries_box.setAccelerated(True)
        self.retries_box.setRange(0, 9999)

        grid_general.addWidget(label_retries, 1, 0)
        grid_general.addWidget(self.retries_box, 1, 1)

        label_html = QLabel(_('HTML download:'))

        self.html_box = QCheckBox()

        grid_general.addWidget(label_html, 2, 0)
        grid_general.addWidget(self.html_box, 2, 1)

        label_conn = QLabel(_('Connections per file:'))

        self.conn_box = QSpinBox()
        #self.retries_box.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.conn_box.setAccelerated(True)
        self.conn_box.setRange(1, 40)

        grid_general.addWidget(label_conn, 3, 0)
        grid_general.addWidget(self.conn_box, 3, 1)

        #
        grid_general.setColumnStretch(2, 1)

    def load(self):
        self.retries_box.setValue(conf.get_retries_limit())
        if conf.get_html_dl():
            self.html_box.toggle()
        self.conn_box.setValue(conf.get_max_conn())

    def save(self):
        limit = str(self.retries_box.value())
        conf.set_retries_limit(limit)
        #
        html = self.html_box.isChecked()
        conf.set_html_dl(html)
        #
        max = str(self.conn_box.value())
        conf.set_max_conn(max)
