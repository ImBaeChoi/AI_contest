import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QDialog, QPushButton
from PyQt5.QtCore import Qt, QPropertyAnimation, QRect, QRectF  # QRectF 추가
from PyQt5 import uic
from PyQt5.QtGui import QMovie, QIcon, QPainterPath, QRegion

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

        # 시그널 연결
        self.hidden_mic_btn.clicked.connect(self.loopAniFuction)
        self.answer_edit.textChanged.connect(self.adjust_dialog_size)
        
        # toolButton 클릭 시 새 창 열기
        self.toolButton.clicked.connect(self.open_new_dialog)

    def loopAniFuction(self):  # 애니메이션 실행 및 ScrollArea 토글 함수
        if self.movie.state() == QMovie.Running:
            self.movie.stop()
            self.scrollArea.setVisible(False)  # 애니메이션 중지 시 ScrollArea 숨김
        else: 
            self.movie.start()
            self.scrollArea.setVisible(True)   # 애니메이션 시작 시 ScrollArea 표시

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

    def open_new_dialog(self):  # 새 창을 여는 함수
        print("ToolButton clicked - Opening new dialog")  # 디버그 메시지
        self.dialog = CustomDialog()
        self.dialog.show()
        self.dialog.exec_()  # 모달 창으로 실행

class CustomDialog(QDialog, dialog_form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # 상단 바 제거
        self.setWindowFlag(Qt.FramelessWindowHint)

        # toggle_btn1, toggle_btn2 초기 설정
        self.setup_toggle_button(self.toggle_btn1)
        self.setup_toggle_button(self.toggle_btn2)

        # 시그널 연결
        self.toggle_btn1.clicked.connect(lambda: self.toggle(self.toggle_btn1))
        self.toggle_btn2.clicked.connect(lambda: self.toggle(self.toggle_btn2))

    def apply_rounded_corners(self, radius=20):  # 둥근 모서리 적용 함수
        rect = QRectF(0, 0, self.width(), self.height())
        path = QPainterPath()
        path.addRoundedRect(rect, radius, radius)
        region = QRegion(path.toFillPolygon().toPolygon())
        self.setMask(region)

    def setup_toggle_button(self, button):
        # 초기 상태 및 스타일 설정
        button.setCheckable(True)
        button.setFixedSize(100, 50)
        button.setStyleSheet("""
            QPushButton {
                background-color: lightgray;
                border-radius: 25px;
                font-weight: bold;
            }
        """)
        button.setText("    OFF")
        button.move(0, 0)
        # 스위치 역할을 하는 작은 버튼 추가
        button.switch = QPushButton(button)
        button.switch.setFixedSize(40, 40)
        button.switch.setStyleSheet("""
            QPushButton {
                background-color: white;
                border-radius: 20px;
            }
        """)
        button.switch.move(5, 5)  # OFF 상태 초기 위치

    def toggle(self, button):
        # 애니메이션 설정
        if button.isChecked():
            # ON 상태
            button.setText("ON    ")
            button.setStyleSheet("""
                QPushButton {
                    background-color: #8BC34A;  /* 밝은 초록색 */
                    color: white;
                    border-radius: 25px;
                    font-weight: bold;
                }
            """)
            start_pos = button.switch.geometry().left()
            end_pos = 55  # 스위치 버튼이 오른쪽으로 이동할 위치 (ON 상태)
        else:
            # OFF 상태
            button.setText("    OFF")
            button.setStyleSheet("""
                QPushButton {
                    background-color: lightgray;
                    color: black;
                    border-radius: 25px;
                    font-weight: bold;
                }
            """)
            start_pos = button.switch.geometry().left()
            end_pos = 5  # 스위치 버튼이 왼쪽으로 이동할 위치 (OFF 상태)

        # 애니메이션 효과
        self.animation = QPropertyAnimation(button.switch, b"geometry")
        self.animation.setDuration(300)  # 애니메이션 지속 시간
        self.animation.setStartValue(QRect(start_pos, 5, 40, 40))
        self.animation.setEndValue(QRect(end_pos, 5, 40, 40))
        self.animation.start()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = WindowClass()
    myWindow.show()
    app.exec_()
