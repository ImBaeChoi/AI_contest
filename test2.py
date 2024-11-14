import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel
from PyQt5 import uic
from PyQt5.QtGui import QMovie, QIcon, QPainterPath, QRegion
from PyQt5.QtCore import Qt, QRectF

form_class = uic.loadUiType("test2.ui")[0]

class WindowClass(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
        # 루프 애니메이션 설정
        self.movie = QMovie("ani.gif")
        self.loopAni.setMovie(self.movie)
        self.movie.setSpeed(200)
        self.movie.start()
        self.movie.stop()

        # 상단 바 제거
        self.setWindowFlag(Qt.FramelessWindowHint)

        # 둥근 모서리 적용
        self.apply_rounded_corners()

        # 우측 하단 고정 위치로 이동
        self.move_to_bottom_right()

        # 시그널 연결
        self.hidden_mic_btn.clicked.connect(self.loopAniFuction)
        self.answer_edit.textChanged.connect(self.adjust_dialog_size)

    def loopAniFuction(self):  # 애니메이션 실행 함수
        if self.movie.state() == QMovie.Running:
            self.movie.stop()
        else: 
            self.movie.start()

    def apply_rounded_corners(self, radius=20):  # 둥근 모서리 적용 함수
        rect = QRectF(0, 0, self.width(), self.height())
        path = QPainterPath()
        path.addRoundedRect(rect, radius, radius)
        region = QRegion(path.toFillPolygon().toPolygon())
        self.setMask(region)

    def resizeEvent(self, event):  # 창 크기 변경 시 둥근 모서리 재적용
        super().resizeEvent(event)
        self.apply_rounded_corners()

    def move_to_bottom_right(self):  # 우측 하단 고정 함수
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()

        window_width = self.width()
        window_height = self.height()

        x = screen_width - window_width
        y = screen_height - window_height
        self.move(x, y)

    def adjust_dialog_size(self):  # 텍스트 길이에 따른 창 높이 조정 및 우측 하단 고정 함수
        document_height = self.answer_edit.document().size().height()
        new_height = max(544, min(int(document_height) + 250, 800))
        current_size = self.size()

        self.resize(current_size.width(), new_height)

        screen_geometry = QApplication.primaryScreen().availableGeometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()

        x = screen_width - self.width()
        y = screen_height - self.height()

        self.move(x, y)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = WindowClass()
    myWindow.show()
    app.exec_()
