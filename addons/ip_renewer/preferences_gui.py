import sys
import logging
logger = logging.getLogger(__name__)

from core.conf_parser import conf
import core.cons as cons

from PySide.QtGui import *
from PySide.QtCore import *

#Config parser
OPTION_IP_RENEW_ACTIVE = "ip_renew_active"
OPTION_IP_RENEW_SCRIPT_PATH = "ip_renew_script_path"
OPTION_RENEW_SCRIPT_ACTIVE = "renew_script_active"


class Preferences(QVBoxLayout):
    """"""
    def __init__(self):
        """"""
        QVBoxLayout.__init__(self)
        
        self.radio_renew = QRadioButton(_('IP Renew (default)'))
        self.radio_script = QRadioButton(_('Run Custom Script'))
        self.radio_renew.toggled.connect(self.on_toggled) #no need to connect script.
        
        self.addWidget(self.radio_renew)
        self.addWidget(self.radio_script)
        
        hbox_script = QHBoxLayout()
        
        label_script_path = QLabel(_('Path:'))
        self.entry_script_path = QLineEdit()
        self.entry_script_path.setFixedHeight(35)
        btn_examine = QPushButton('...')
        btn_examine.clicked.connect(self.on_examine)
        btn_examine.setFixedHeight(35)
        btn_examine.setMaximumWidth(80)
        
        hbox_script.addWidget(label_script_path)
        hbox_script.addWidget(self.entry_script_path)
        hbox_script.addWidget(btn_examine)
        
        self.addLayout(hbox_script)
        
        self.addStretch()
        
        self.script_widgets_tuple = (label_script_path, self.entry_script_path, btn_examine)
    
    def on_toggled(self):
        if self.radio_script.isChecked():
            [widget.setEnabled(True) for widget in self.script_widgets_tuple]
        else:
            [widget.setEnabled(False) for widget in self.script_widgets_tuple]
    
    def on_examine(self):
        file_name, filter = QFileDialog.getOpenFileName()
        if file_name:
            self.entry_script_path.setText(file_name)
    
    def load(self):
        if conf.get_addon_option(OPTION_RENEW_SCRIPT_ACTIVE, default=False, is_bool=True):
            self.radio_script.setChecked(True) #emits toggle.
        else:
            self.radio_renew.setChecked(True)
        path = conf.get_addon_option(OPTION_IP_RENEW_SCRIPT_PATH, default="")
        self.entry_script_path.setText(path)
    
    def save(self):
        if self.radio_script.isChecked():
            conf.set_addon_option(OPTION_RENEW_SCRIPT_ACTIVE, "True")
        else:
            conf.set_addon_option(OPTION_RENEW_SCRIPT_ACTIVE, "False")
        path = self.entry_script_path.text()
        conf.set_addon_option(OPTION_IP_RENEW_SCRIPT_PATH, path)


