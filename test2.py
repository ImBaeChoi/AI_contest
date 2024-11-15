import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QDialog, QPushButton
from PyQt5.QtCore import Qt, QPropertyAnimation, QRect, QRectF
from PyQt5 import uic
from PyQt5.QtGui import QMovie, QPainterPath, QRegion

form_class = uic.loadUiType("test2.ui")[0]  # 메인 UI 로드
dialog_form_class = uic.loadUiType("new_dialog.ui")[0]  # 옵션 UI 로드
exit_dialog_form_class = uic.loadUiType("exit.ui")[0]  # 종료 UI 로드

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

        # ScrollArea를 초기에는 숨김
        self.scrollArea.setVisible(False)

        # 상단 바 제거
        self.setWindowFlag(Qt.FramelessWindowHint)

        # 둥근 모서리 적용
        self.apply_rounded_corners()

        # 우측 하단 고정 위치로 이동
        self.move_to_bottom_right()

        # 시그널 연결
        self.hidden_mic_btn.clicked.connect(self.loopAniFuction)
        self.answer_edit.textChanged.connect(self.adjust_dialog_size)

        # toolButton 클릭 시 새 창 열기
        self.toolButton.clicked.connect(lambda: self.open_new_dialog(CustomDialog))

        # exitButton이 있는 경우에만 연결
        if hasattr(self, "exitButton"):
            self.exitButton.clicked.connect(lambda: self.open_new_dialog(ExitDialog))

    def loopAniFuction(self):
        if self.movie.state() == QMovie.Running:
            self.movie.stop()
            self.scrollArea.setVisible(False)
        else:
            self.movie.start()
            self.scrollArea.setVisible(True)

    def apply_rounded_corners(self, radius=20):
        rect = QRectF(0, 0, self.width(), self.height())
        path = QPainterPath()
        path.addRoundedRect(rect, radius, radius)
        region = QRegion(path.toFillPolygon().toPolygon())
        self.setMask(region)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.apply_rounded_corners()

    def move_to_bottom_right(self):
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()

        window_width = self.width()
        window_height = self.height()

        x = screen_width - window_width
        y = screen_height - window_height
        self.move(x, y)

    def adjust_dialog_size(self):
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

    def open_new_dialog(self, dialog_class):
        dialog = dialog_class()
        dialog.exec_()

# 옵션 창 클래스
class CustomDialog(QDialog, dialog_form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # 상단 바 제거
        self.setWindowFlag(Qt.FramelessWindowHint)

        # 둥근 모서리 적용
        self.apply_rounded_corners()

        # 시그널 연결
        self.toggle_btn1.clicked.connect(lambda: self.toggle(self.toggle_btn1, self.btn1_btn))
        self.toggle_btn2.clicked.connect(lambda: self.toggle(self.toggle_btn2, self.btn2_btn))

    def apply_rounded_corners(self, radius=20):
        rect = QRectF(0, 0, self.width(), self.height())
        path = QPainterPath()
        path.addRoundedRect(rect, radius, radius)
        region = QRegion(path.toFillPolygon().toPolygon())
        self.setMask(region)

    def toggle(self, button, sbtn):
        y_position = sbtn.geometry().top()

        if button.isChecked():
            button.setText("ON")
            button.setStyleSheet("""
                QPushButton {
                    background-color: #8BC34A;
                    color: white;
                    border-radius: 25px;
                    font-weight: bold;
                }
            """)
            start_pos = sbtn.geometry().left()
            end_pos = 88  # 오른쪽으로 이동
        else:
            button.setText("OFF")
            button.setStyleSheet("""
                QPushButton {
                    background-color: lightgray;
                    color: black;
                    border-radius: 25px;
                    font-weight: bold;
                }
            """)
            start_pos = sbtn.geometry().left()
            end_pos = 38  # 왼쪽으로 이동

        self.animation = QPropertyAnimation(sbtn, b"geometry")
        self.animation.setDuration(300)
        self.animation.setStartValue(QRect(start_pos, y_position, 40, 40))
        self.animation.setEndValue(QRect(end_pos, y_position, 40, 40))
        self.animation.start()

class ExitDialog(QDialog, exit_dialog_form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # 상단 바 제거
        self.setWindowFlag(Qt.FramelessWindowHint)

        # 둥근 모서리 적용
        self.apply_rounded_corners()

    def apply_rounded_corners(self, radius=20):
        rect = QRectF(0, 0, self.width(), self.height())
        path = QPainterPath()
        path.addRoundedRect(rect, radius, radius)
        region = QRegion(path.toFillPolygon().toPolygon())
        self.setMask(region)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = WindowClass()
    myWindow.show()
    app.exec_()
