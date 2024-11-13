import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel
from PyQt5 import uic
from PyQt5.QtGui import QMovie,QIcon

form_class = uic.loadUiType("test2.ui")[0]

class WindowClass(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
        self.movie = QMovie("ani.gif")
        self.loopAni.setMovie(self.movie)
        self.movie.setSpeed(200)
        self.movie.start()
        self.movie.stop()

        self.mic_btn.clicked.connect(self.loopAniFuction)
        self.hidden_mic_btn.clicked.connect(self.loopAniFuction)
        
    def loopAniFuction(self):    
        if self.movie.state() == QMovie.Running:
            self.movie.stop()
        else: self.movie.start()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = WindowClass()
    myWindow.show()
    app.exec_()