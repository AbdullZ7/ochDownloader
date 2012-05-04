from core.config import config_parser

from PySide.QtGui import *
from PySide.QtCore import *


class General(QGroupBox):
    def __init__(self, parent=None):
        QGroupBox.__init__(self, 'General:')

        #vbox_general = QVBoxLayout()
        grid_general = QGridLayout()
        self.setLayout(grid_general)

        label_retries = QLabel('Retries limit:')
        #label_retries.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.retries_box = QSpinBox()
        #self.retries_box.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.retries_box.setAccelerated(True)
        self.retries_box.setRange(0, 9999)

        grid_general.addWidget(label_retries, 1, 0)
        grid_general.addWidget(self.retries_box, 1, 1)
        grid_general.setColumnStretch(2, 1)

    def load(self):
        retries_limit = config_parser.get_retries_limit()
        self.retries_box.setValue(retries_limit)

    def save(self):
        limit = str(self.retries_box.value())
        config_parser.set_retries_limit(limit)
