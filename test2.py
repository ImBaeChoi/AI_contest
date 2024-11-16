import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QDialog, QPushButton
from PyQt5.QtCore import Qt, QPropertyAnimation, QRect, QRectF
from PyQt5 import uic
from PyQt5.QtGui import QMovie, QIcon, QPainterPath, QRegion

# 다크 모드와 라이트 모드 스타일
DARK_MODE_STYLE = """
    QWidget {
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, 
                                    stop: 0 #9b3d3d, stop: 1 #3b5c91); /* 어두운 핑크색에서 어두운 파란색으로 그라데이션 */
        color: white;
    }
    QPushButton {
        background-color: #333;
        color: white;
        border-radius: 5px;
    }
"""
LIGHT_MODE_STYLE = """
    QWidget {
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #ffb3b3, stop: 1 #87cefa);
        color: black;
    }
    QPushButton {
        background-color: #f0f0f0;
        color: black;
        border-radius: 5px;
    }
"""

form_class = uic.loadUiType("test2.ui")[0]  # 메인 UI 로드
dialog_form_class = uic.loadUiType("new_dialog.ui")[0]  # 옵션 UI 로드

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

        # 초기 모드 설정
        self.current_mode = "light"  # "light" 모드로 초기화
        self.setStyleSheet(LIGHT_MODE_STYLE)  # 초기 스타일을 라이트 모드로 설정

        # 시그널 연결
        self.hidden_mic_btn.clicked.connect(self.loopAniFuction)
        self.answer_edit.textChanged.connect(self.adjust_dialog_size)
        
        # toolButton 클릭 시 새 창 열기
        self.toolButton.clicked.connect(self.open_new_dialog)

    def loopAniFuction(self):  # 애니메이션 실행 및 ScrollArea 토글 함수
        if self.movie.state() == QMovie.Running:
            self.movie.stop()
            self.scrollArea.setVisible(False)
        else: 
            self.movie.start()
            self.scrollArea.setVisible(True)

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

    def open_new_dialog(self):  # 옵션 창을 여는 함수
        self.dialog = CustomDialog(self.current_mode, self)  # 현재 모드 값을 전달
        self.dialog.show()
        self.dialog.exec_()

    def toggle_mode(self):  # 다크 모드/라이트 모드 전환
        if self.current_mode == "light":
            self.setStyleSheet(DARK_MODE_STYLE)  # 다크 모드로 변경
            self.current_mode = "dark"  # 현재 모드 상태를 "dark"로 변경
        else:
            self.setStyleSheet(LIGHT_MODE_STYLE)  # 라이트 모드로 변경
            self.current_mode = "light"  # 현재 모드 상태를 "light"로 변경

# 옵션 창 클래스
class CustomDialog(QDialog, dialog_form_class):
    def __init__(self, current_mode, main_window):
        super().__init__()
        self.setupUi(self)

        # 받은 current_mode 값 설정
        self.current_mode = current_mode
        self.main_window = main_window  # 메인 윈도우 참조

        # 초기 모드에 맞게 스타일 적용
        self.apply_mode(current_mode)

        # 상단 바 제거
        self.setWindowFlag(Qt.FramelessWindowHint)

        # 둥근 모서리 적용
        self.apply_rounded_corners()

        # 시그널 연결
        self.toggle_btn1.clicked.connect(lambda: self.toggle(self.toggle_btn1, self.btn1_btn))
        self.toggle_btn2.clicked.connect(lambda: self.toggle(self.toggle_btn2, self.btn2_btn))

    def apply_mode(self, mode):
        """다크 모드와 라이트 모드 스타일을 설정하는 함수"""
        if mode == "dark":
            self.setStyleSheet(DARK_MODE_STYLE)
        else:
            self.setStyleSheet(LIGHT_MODE_STYLE)

    def apply_rounded_corners(self, radius=20):  # 둥근 모서리 적용 함수
        rect = QRectF(0, 0, self.width(), self.height())
        path = QPainterPath()
        path.addRoundedRect(rect, radius, radius)
        region = QRegion(path.toFillPolygon().toPolygon())
        self.setMask(region)

    def toggle(self, button, sbtn):  # 옵션 버튼 함수
        y_position = sbtn.geometry().top()

        if button.isChecked():
            button.setText("ON    ")
            button.setStyleSheet("""
                QPushButton {
                    background-color: #8BC34A;
                    color: white;
                    border-radius: 25px;
                    font-weight: bold;
                }
            """)
            start_pos = sbtn.geometry().left()
            end_pos = 95  # 스위치 버튼이 오른쪽으로 이동 (ON 상태)
        else:
            button.setText("    OFF")
            button.setStyleSheet("""
                QPushButton {
                    background-color: lightgray;
                    color: black;
                    border-radius: 25px;
                    font-weight: bold;
                }
            """)
            start_pos = sbtn.geometry().left()
            end_pos = 45  # 스위치 버튼이 왼쪽으로 이동 (OFF 상태)

        self.animation = QPropertyAnimation(sbtn, b"geometry")
        self.animation.setDuration(300)  # 애니메이션 지속 시간
        self.animation.setStartValue(QRect(start_pos, y_position, 40, 40))
        self.animation.setEndValue(QRect(end_pos, y_position, 40, 40))
        self.animation.start()

        # 다크 모드/라이트 모드 전환
        if button == self.toggle_btn1:
            self.toggle_mode()  # 옵션 창 내에서의 모드 변경

    def toggle_mode(self):  # 다크 모드/라이트 모드 전환
        if self.current_mode == "light":
            self.setStyleSheet(DARK_MODE_STYLE)  # 다크 모드로 변경
            self.current_mode = "dark"  # 현재 모드 상태를 "dark"로 변경
            self.main_window.toggle_mode()  # 메인 창 모드도 함께 변경
        else:
            self.setStyleSheet(LIGHT_MODE_STYLE)  # 라이트 모드로 변경
            self.current_mode = "light"  # 현재 모드 상태를 "light"로 변경
            self.main_window.toggle_mode()  # 메인 창 모드도 함께 변경

if __name__ == "__main__":  
    app = QApplication(sys.argv)
    myWindow = WindowClass()
    myWindow.show()
    app.exec_()
