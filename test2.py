import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QDialog, QPushButton
from PyQt5.QtCore import Qt, QPropertyAnimation, QRect, QRectF, QTimer
from PyQt5 import uic
from PyQt5.QtGui import QMovie, QPainterPath, QRegion, QLinearGradient, QBrush, QColor, QPalette

# 다크 모드와 라이트 모드 스타일
DARK_MODE_STYLE = """
    QWidget {
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, 
                                    stop: 0 #9b3d3d, stop: 1 #3b5c91);
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
options_dialog_form_class = uic.loadUiType("options_dialog.ui")[0]  # 옵션 UI 로드
exit_dialog_form_class = uic.loadUiType("exit_dialog.ui")[0]

class WindowClass(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # 상단 바 제거
        self.setWindowFlag(Qt.FramelessWindowHint)

        # 둥근 모서리 적용
        self.apply_rounded_corners()

        # 우측 하단 고정 위치로 이동
        self.move_to_bottom_right()

        # 초기 모드 설정
        self.current_mode = "light"
        self.setStyleSheet(LIGHT_MODE_STYLE)
        
        # 상태 저장 변수 추가
        self.dialog_toggle_states = {"toggle_btn1": False, "toggle_btn2": False}
        self.options_dialog = None

        # toolButton 클릭 시 대화 상자 열거나 닫기
        self.toolButton.clicked.connect(self.toggle_options_dialog)

        #애니메이션 관리
        self.make_widget_rounded(self.loopAni)
        self.gradient_offset = 0
        self.update_gradient()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate_gradient)
        self.timer.start(13)

        self.hidden_mic_btn.clicked.connect(self.mic)

    def mic(slef):
        print("마이크 버튼 클릭")    

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

    def open_new_dialog(self, dialog_class): #새 다이어로그 열기
        self.options_dialog = dialog_class(self.current_mode, self.dialog_toggle_states, self)
        main_window_geometry = self.geometry()
        x = main_window_geometry.x() - self.options_dialog.width() - 10
        y = main_window_geometry.y()
        self.options_dialog.move(x, y)
        self.options_dialog.show()

        self.options_dialog.finished.connect(self.save_dialog_states)


    def toggle_mode(self):  # 다크 모드/라이트 모드 전환
        if self.current_mode == "light":
            self.setStyleSheet(DARK_MODE_STYLE)
            self.current_mode = "dark"
        else:
            self.setStyleSheet(LIGHT_MODE_STYLE)
            self.current_mode = "light"
     
    def animate_gradient(self):
        """그라데이션을 매끄럽게 주기적으로 업데이트"""
        self.gradient_offset += 0.002  # 매우 작은 값으로 점진적으로 증가
        if self.gradient_offset >= 3.0:  # 더 큰 범위를 사용하여 자연스러운 순환
            self.gradient_offset -= 3.0  # 주기를 초과하면 순환되도록 설정

        self.update_gradient()

    def update_gradient(self):
        """loopAni 위젯에 그라데이션 색상 업데이트"""
        gradient = QLinearGradient(0, 0, self.loopAni.width(), self.loopAni.height())

        # 색상 조합을 자연스럽게 배치하여 매끄러운 전환
        gradient.setColorAt((self.gradient_offset + 0.0) % 1.0, QColor("#FFB3B3"))  # 밝은 핑크색
        gradient.setColorAt((self.gradient_offset + 0.33) % 1.0, QColor("#87CEFA"))  # 하늘색
        gradient.setColorAt((self.gradient_offset + 0.66) % 1.0, QColor("#FFB3B3"))  # 밝은 노란색

        # 브러시를 설정하여 loopAni 배경 적용
        palette = self.loopAni.palette()
        palette.setBrush(QPalette.Background, QBrush(gradient))
        self.loopAni.setAutoFillBackground(True)
        self.loopAni.setPalette(palette)


        # 브러시를 설정하여 loopAni 배경 적용
        palette = self.loopAni.palette()
        palette.setBrush(QPalette.Background, QBrush(gradient))
        self.loopAni.setAutoFillBackground(True)
        self.loopAni.setPalette(palette)


    def make_widget_rounded(self, widget, radius=50):
        """위젯의 모양을 둥글게 설정"""
        rect = widget.geometry()
        path = QPainterPath()
        path.addRoundedRect(0, 0, rect.width(), rect.height(), radius, radius)
        region = QRegion(path.toFillPolygon().toPolygon())
        widget.setMask(region)

    def toggle_options_dialog(self):
        # 대화 상자가 열려 있으면 닫기
        if self.options_dialog and self.options_dialog.isVisible():
            self.options_dialog.close()
            self.options_dialog = None
        else:
            # 대화 상자가 닫혀 있으면 열기
            self.open_new_dialog(CustomDialog)

    def save_dialog_states(self):
        # 대화 상자 종료 시 상태 저장
        if self.options_dialog:
            self.dialog_toggle_states = self.options_dialog.get_toggle_states()
            self.options_dialog = None

class CustomDialog(QDialog, options_dialog_form_class):
    def __init__(self, current_mode, toggle_states, main_window):
        super().__init__()
        self.setupUi(self)

        # 받은 current_mode 값 설정
        self.current_mode = current_mode
        self.main_window = main_window
        self.toggle_states = toggle_states

        # 초기 모드에 맞게 스타일 적용
        self.apply_mode(current_mode)

        # 상단 바 제거
        self.setWindowFlag(Qt.FramelessWindowHint)

        # 둥근 모서리 적용
        self.apply_rounded_corners()

        # 상태 복원
        self.toggle_btn1.setChecked(self.toggle_states["toggle_btn1"])
        self.toggle_btn2.setChecked(self.toggle_states["toggle_btn2"])
        self.update_toggle_style(self.toggle_btn1, self.btn1_btn)
        self.update_toggle_style(self.toggle_btn2, self.btn2_btn)

        # 시그널 연결
        self.toggle_btn1.clicked.connect(lambda: self.toggle(self.toggle_btn1, self.btn1_btn))
        self.toggle_btn2.clicked.connect(lambda: self.toggle(self.toggle_btn2, self.btn2_btn))


    def apply_mode(self, mode): #다크모드/라이트모드 설정
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
            button.setText("ON     ")
            button.setStyleSheet("""
                QPushButton {
                    background-color: #8BC34A;
                    color: white;
                    border-radius: 25px;
                    font-weight: bold;
                }
            """)
            start_pos = sbtn.geometry().left()
            end_pos = 85
        else:
            button.setText("       OFF")
            button.setStyleSheet("""
                QPushButton {
                    background-color: lightgray;
                    color: black;
                    border-radius: 25px;
                    font-weight: bold;
                }
            """)
            start_pos = sbtn.geometry().left()
            end_pos = 40

        self.animation = QPropertyAnimation(sbtn, b"geometry")
        self.animation.setDuration(300)
        self.animation.setStartValue(QRect(start_pos, y_position, 40, 40))
        self.animation.setEndValue(QRect(end_pos, y_position, 40, 40))
        self.animation.start()

        if button == self.toggle_btn1:
            self.toggle_mode()

    def toggle_mode(self):  # 다크 모드/라이트 모드 전환
        if self.current_mode == "light":
            self.setStyleSheet(DARK_MODE_STYLE)  # 다크 모드로 변경
            self.current_mode = "dark"  # 현재 모드 상태를 "dark"로 변경
            self.main_window.toggle_mode()  # 메인 창 모드도 함께 변경
        else:
            self.setStyleSheet(LIGHT_MODE_STYLE)  # 라이트 모드로 변경
            self.current_mode = "light"  # 현재 모드 상태를 "light"로 변경
            self.main_window.toggle_mode()  # 메인 창 모드도 함께 변경

    def update_toggle_style(self, button, sbtn):  # 버튼 스타일 업데이트
        if button.isChecked():
            button.setText("ON     ")
            button.setStyleSheet("""
                QPushButton {
                    background-color: #8BC34A;
                    color: white;
                    border-radius: 25px;
                    font-weight: bold;
                }
            """)
            sbtn.setGeometry(85, sbtn.geometry().top(), 40, 40)  # 오른쪽으로 이동
        else:
            button.setText("       OFF")
            button.setStyleSheet("""
                QPushButton {
                    background-color: lightgray;
                    color: black;
                    border-radius: 25px;
                    font-weight: bold;
                }
            """)
            sbtn.setGeometry(40, sbtn.geometry().top(), 40, 40)  # 왼쪽으로 이동

    def get_toggle_states(self):  # 현재 토글 버튼 상태 반환
        return {
            "toggle_btn1": self.toggle_btn1.isChecked(),
            "toggle_btn2": self.toggle_btn2.isChecked()
        }

class ExitClass(QMainWindow, exit_dialog_form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.exit_btn.clicked.connect(self.exit)
        self.cancel_btn.clicked.connect(self.connect)

    def exit(self):
        print("Vesta를 종료합니다")

    def cancel(self):
        print("종료를 취소합니다")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = WindowClass()
    myWindow.show()
    sys.exit(app.exec_())
