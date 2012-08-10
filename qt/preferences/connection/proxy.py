import core.cons as cons
from core.conf_parser import conf
from core.network.connection import request

from PySide.QtGui import *
from PySide.QtCore import *


class Proxy(QGroupBox):
    def __init__(self, parent=None):
        QGroupBox.__init__(self, 'Proxy:')

        vbox_proxy = QVBoxLayout()
        self.setLayout(vbox_proxy)

        self.radio_without = QRadioButton('Without proxy')
        self.radio_manual = QRadioButton('Manual proxy config')
        self.radio_without.toggled.connect(self.on_toggled) #no need to connect manual.

        vbox_proxy.addWidget(self.radio_without)
        vbox_proxy.addWidget(self.radio_manual)

        hbox_proxy = QHBoxLayout()

        label_http_proxy = QLabel('HTTP Proxy:')
        self.entry_proxy_ip = QLineEdit()

        hbox_proxy.addWidget(label_http_proxy)
        hbox_proxy.addWidget(self.entry_proxy_ip)

        label_http_port = QLabel('Port:')
        self.port_box = QSpinBox()
        self.port_box.setAccelerated(True)
        self.port_box.setRange(0, 9999)

        hbox_proxy.addWidget(label_http_port)
        hbox_proxy.addWidget(self.port_box)

        vbox_proxy.addLayout(hbox_proxy)

        self.proxy_widgets_tuple = (label_http_proxy, self.entry_proxy_ip, label_http_port, self.port_box)

    def on_toggled(self):
        if self.radio_manual.isChecked():
            [widget.setEnabled(True) for widget in self.proxy_widgets_tuple]
        else:
            [widget.setEnabled(False) for widget in self.proxy_widgets_tuple]

    def load(self):
        proxy = conf.get_proxy()
        if proxy is not None:
            ptype, ip, port = proxy
            self.port_box.setValue(port)
            self.entry_proxy_ip.setText(ip)
            if conf.get_proxy_active():
                self.radio_manual.setChecked(True) #emit toggled.
            else:
                self.radio_without.setChecked(True)

    def save(self):
        ptype, ip, port = cons.PROXY_HTTP, self.entry_proxy_ip.text(), str(self.port_box.value())
        conf.set_proxy(ptype, ip, port)

        if self.radio_manual.isChecked():
            conf.set_proxy_active("True")
            request.set_proxy(ptype, ip, port)
        else:
            conf.set_proxy_active("False")
            request.no_proxy()
