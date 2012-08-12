from PySide.QtGui import *
from PySide.QtCore import *

from general import General


class GUI(QScrollArea):
    def __init__(self, parent=None):
        QScrollArea.__init__(self)
        self.setWidgetResizable(True)
        self.setEnabled(True)

        self.widgets = []

        self.vbox = QVBoxLayout()
        #self.setContentsMargins(0, 0, 0, 0)
        self.vbox.setSpacing(5)
        self.vbox_widget = QWidget()
        self.vbox_widget.setLayout(self.vbox)
        self.setWidget(self.vbox_widget)

        self.general = General()
        self.vbox.addWidget(self.general)
        self.widgets.append(self.general)

        self.vbox.addStretch(0)

    def load(self):
        for widget in self.widgets: #polymorphism.
            widget.load()

    def save(self):
        for widget in self.widgets: #polymorphism.
            widget.save()
