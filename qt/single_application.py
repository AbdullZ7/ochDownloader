import sys

from PySide.QtGui import QMessageBox, QApplication
from PySide.QtCore import QIODevice
from PySide.QtNetwork import QLocalServer, QLocalSocket


class QSingleApplication:
    def __init__(self, app, app_id):
        # create local socket. If cant connect, create local server
        self.app = app
        self.app_id = app_id
        self.can_run = False
        self.create_socket()

    def create_socket(self):
        self.socket = QLocalSocket()
        self.socket.connected.connect(self.on_connected)
        self.socket.error.connect(self.create_server)
        self.socket.connectToServer(self.app_id, QIODevice.WriteOnly)

    def on_connected(self):
        if len(sys.argv) > 1 and sys.argv[1] is not None:
            self.socket.write(sys.argv[1])
            self.socket.bytesWritten.connect(self.app.quit)
        else:
            QMessageBox.warning(None, "Already running", "The program is already running.")
            self.app.quit()

    def create_server(self):
        self.server = QLocalServer()
        self.can_run = True
        if self.server.listen(self.app_id):
            self.server.newConnection.connect(self.on_new_connection)
        else:
            # cant listen the socket, create multiple instances then
            QMessageBox.critical(None, "Error", "Error listening the socket.")

    def on_new_connection(self):
        self.new_socket = self.server.nextPendingConnection()
        self.new_socket.readyRead.connect(self.readSocket)

    def readSocket(self):
        f = self.new_socket.readLine()
        #str(f)


if __name__ == '__main__':
    from PySide.QtGui import QMainWindow, QLabel

    class GUI(QMainWindow):
        def __init__(self):
            QMainWindow.__init__(self)
            self.setWindowTitle("QSingleApplication Demo")
            labelText = "demo app"
            self.setCentralWidget(QLabel(labelText))
            self.show()

    app = QApplication(sys.argv) #QApplication(sys.argv)
    ss = QSingleApplication(app, app_id="ochDownloader")
    if ss.can_run:
        gui = GUI()
    sys.exit(app.exec_())