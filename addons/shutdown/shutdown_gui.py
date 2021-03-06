
from shutdown import Shutdown
import core.cons as cons
from core import events

from PySide.QtGui import *
from PySide.QtCore import *

if cons.OS_WIN:
    from qt.misc import flash_wnd
else:
    flash_wnd = None

TIME_OUT = 60


class ShutdownDialog(QMessageBox):
    def __init__(self, parent):
        QMessageBox.__init__(self, parent)
        self.setWindowTitle(_('Shutting down'))
        
        #self.setIconPixmap(QPixmap('ochdownload2.png'))
        
        self.setText(_("The system is going to shut down."))

        btn_cancel = self.addButton(QMessageBox.Cancel)
        btn_cancel.clicked.connect(self.reject)
        self.setDefaultButton(QMessageBox.Cancel)
        #self.setEscapeButton(QMessageBox.Cancel)
        
        self.timeout = TIME_OUT
        
        self.timer = parent.idle_timeout(1000, self.update_)

        #Flash if the window is in the background.
        if flash_wnd is not None:
            flash_wnd.flash_taskbar_icon(parent.winId())

        self.exec_()
        self.deleteLater()

    def reject(self, *args, **kwargs):
        self.timer.stop()
        self.hide()
        QDialog.reject(self, *args, **kwargs)

    def update_(self):
        if self.timeout > 0:
            self.timeout -= 1
            self.setInformativeText("{} {}".format(_("Shutting in"), self.timeout))
        else:
            shutdown = Shutdown()
            if shutdown.start_shutting():
                events.quit.emit()
            self.timer.stop()
