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
        self.current_mode = "light"  # "light" 모드로 초기화
        self.setStyleSheet(LIGHT_MODE_STYLE)  # 초기 스타일을 라이트 모드로 설정
        
        # 상태 저장 변수 추가
        self.dialog_toggle_states = {"toggle_btn1": False, "toggle_btn2": False}

        # toolButton 클릭 시 새 창 열기
        self.toolButton.clicked.connect(lambda: self.open_new_dialog(CustomDialog))


        self.make_widget_rounded(self.loopAni)
        self.gradient_offset = 0
        self.update_gradient()

        # 그라데이션 애니메이션 타이머
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate_gradient)
        self.timer.start(13)  # 50ms마다 실행

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

    def open_new_dialog(self, dialog_class):
        # CustomDialog를 생성할 때 current_mode, toggle_states, main_window를 전달
        dialog = dialog_class(self.current_mode, self.dialog_toggle_states, self)
        # 대화 상자의 위치 설정
        main_window_geometry = self.geometry()  # 현재 메인 창의 위치와 크기 가져오기
        x = main_window_geometry.x() - dialog.width() - 10  # 메인 창의 왼쪽에 배치, 10px 간격
        y = main_window_geometry.y()  # 동일한 y 좌표로 배치
        dialog.move(x, y)  # CustomDialog 위치 설정
        dialog.exec_()

        # 대화 상자 종료 후 상태 저장
        self.dialog_toggle_states = dialog.get_toggle_states()


    def toggle_mode(self):  # 다크 모드/라이트 모드 전환
        if self.current_mode == "light":
            self.setStyleSheet(DARK_MODE_STYLE)  # 다크 모드로 변경
            self.current_mode = "dark"  # 현재 모드 상태를 "dark"로 변경
        else:
            self.setStyleSheet(LIGHT_MODE_STYLE)  # 라이트 모드로 변경
            self.current_mode = "light"  # 현재 모드 상태를 "light"로 변경

    def closeEvent(self, event):  # 애플리케이션 종료 처리
        if self.movie.state() == QMovie.Running:
            self.movie.stop()
        self.movie.deleteLater()  # QMovie 자원 해제
        super().closeEvent(event)
    
    
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

class CustomDialog(QDialog, options_dialog_form_class):
    def __init__(self, current_mode, toggle_states, main_window):
        super().__init__()
        self.setupUi(self)

        # 받은 current_mode 값 설정
        self.current_mode = current_mode
        self.main_window = main_window  # 메인 윈도우 참조
        self.toggle_states = toggle_states  # 상태 값 가져오기

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

        self.close_btn.clicked.connect(self.close)

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
            end_pos = 85  # 스위치 버튼이 오른쪽으로 이동 (ON 상태)
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
            end_pos = 40  # 스위치 버튼이 왼쪽으로 이동 (OFF 상태)

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



if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = WindowClass()
    myWindow.show()
    sys.exit(app.exec_())
