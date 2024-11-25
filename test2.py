import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QDialog, QGraphicsDropShadowEffect, QWidget, QTextEdit
from PyQt5.QtCore import Qt, QPropertyAnimation, QRect, QRectF, QTimer,QEasingCurve
from PyQt5 import uic
from PyQt5.QtGui import QPainterPath, QRegion, QLinearGradient, QBrush, QColor, QPalette, QIcon, QFontDatabase, QFont

# 다크 모드와 라이트 모드 스타일
DARK_MODE_STYLE = """
    QWidget {
        background-color: #060913;  /* Dialog 배경색 설정 */
        color: white;
    }
    QPushButton {
        background-color: #6A5ACD;
        color: white;
        border-radius: 5px;
    }
    QLabel {
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, 
                                    stop: 0 #0D101D, stop: 1 #161926); /* 어두운 그라데이션 */
        color: white;  /* 텍스트 색상 */
    }
    QTextEdit {
        background-color: #060913;  /* 검은색에 가까운 회색 */
        color: white;  /* 텍스트 색상 */
        border: none;  /* 테두리 없음 */
    }
    #textlabel_2, #textlabel_3, #textlabel_4 {
        background-color: #02030B; /* 다크 모드에서 어두운 배경 */
        color: white;  /* 텍스트는 흰색 */
        border: 1px solid #444; /* 약간의 테두리 */
    }
    #loopAni_label {
        background-color: #161926;
    }
"""
LIGHT_MODE_STYLE = """
    QWidget {
        background-color: #FFFFFF;  /* Dialog 배경색 설정 */
        color: black;
    }

    QPushButton {
        background-color: #FFD700;
        color: black;
        border-radius: 5px;
    }
    QLabel {
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, 
                                    stop: 0 #ffe4e1, stop: 1 #AACFE7); /* 밝은 그라데이션 */
        color: black;  /* 텍스트 색상 */
    }
    #textlabel_2, #textlabel_3, #textlabel_4 {
        background-color: #FFFFFF;
    }
    QTextEdit {
        background-color: #F3F4F1;
    }
    #loopAni_label {
        background-color: #FFFFFF;
    }
"""

form_class = uic.loadUiType("test2.ui")[0]  # 메인 UI 로드
options_dialog_form_class = uic.loadUiType("options_dialog.ui")[0]  # 옵션 UI 로드

class WindowClass(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.apply_external_font("textEdit", "AritaBuriKR-HairLine.ttf", font_size=15)
        self.apply_external_font("textEdit_2", "AritaBuriKR-HairLine.ttf", font_size=15)
        self.apply_external_font("textEdit_3", "AritaBuriKR-HairLine.ttf", font_size=15)

        self.slide_in()

        # 초기 라이트 모드로 설정
        self.current_mode = "light"
        self.setStyleSheet(LIGHT_MODE_STYLE)

        # 옵션 버튼 초기 아이콘 설정(라이트)
        self.update_toolbutton_icon()

        # 상단 바 제거
        self.setWindowFlag(Qt.FramelessWindowHint)

        # 메인 창 둥근 모서리 적용
        self.apply_rounded_corners()
        
        # 상태 저장 변수 추가
        self.dialog_toggle_states = {"toggle_btn1": False, "toggle_btn2": False}
        self.options_dialog = None

        # toolButton 클릭 시 옵션 UI 열기, 닫기
        self.toolButton.clicked.connect(self.toggle_options_dialog)

        # 루프 애니메이션 관리
        self.make_widget_rounded(self.loopAni)
        self.make_widget_rounded(self.loopAni_label)
        self.gradient_offset = 0
        self.update_gradient()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate_gradient)
        self.timer.start(8)

        # 위젯에 그림자 효과 추가
        self.add_shadow_effect("textlabel_2")
        self.add_shadow_effect("textlabel_3")
        self.add_shadow_effect("textlabel_4")
        self.add_shadow_effect("toolButton")
        self.add_shadow_effect("loopAni_label")
        self.add_shadow_effect("textEdit",10)
        self.add_shadow_effect("textEdit_2",10)
        self.add_shadow_effect("textEdit_3",10)


    # 텍스트 위젯 애니메이션
    def animate_widgets(self): 
        widgets = [self.hidden_mic_btn, self.loopAni, self.textEdit, self.textEdit_2, self.textEdit_3,
                self.text_label, self.textlabel_2, self.textlabel_3, self.textlabel_4, self.loopAni_label]

        for widget in widgets:
            y_start = widget.geometry().y()
            x = widget.geometry().x()
            width = widget.geometry().width()
            height = widget.geometry().height()

            # 애니메이션 생성
            animation = QPropertyAnimation(widget, b"geometry")
            animation.setDuration(500)  # 애니메이션 지속 시간 (밀리초)
            animation.setStartValue(QRect(x, y_start, width, height))

            # 특정 위젯에 대해 다른 애니메이션 설정
            if widget in [self.hidden_mic_btn, self.loopAni, self.text_label, self.loopAni_label]:
                animation.setEndValue(QRect(x, y_start - 500, width, height))  # 더 멀리 이동
            else:
                animation.setEndValue(QRect(x, y_start - 400, width, height))  # 일반 이동

            # 애니메이션 실행 및 저장
            animation.start()
            self.animations.append(animation)  # 애니메이션을 인스턴스 변수에 저장


    def apply_rounded_corners(self, radius=20):  # 둥근 모서리 적용 함수
        rect = QRectF(0, 0, self.width(), self.height())
        path = QPainterPath()
        path.addRoundedRect(rect, radius, radius)
        region = QRegion(path.toFillPolygon().toPolygon())
        self.setMask(region)

        # 새 UI 열기
    def open_new_dialog(self, dialog_class):
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

        self.update_toolbutton_icon()
     
        # 루프 애니메이션 설정 함수
    def animate_gradient(self):
        self.gradient_offset += 0.002  # 매우 작은 값으로 점진적으로 증가
        if self.gradient_offset >= 3.0:  # 더 큰 범위를 사용하여 자연스러운 순환
            self.gradient_offset -= 3.0  # 주기를 초과하면 순환되도록 설정

        self.update_gradient()

        # 루프 애니메이션 색상 설정 함수
    def update_gradient(self):
        gradient = QLinearGradient(0, 0, self.loopAni.width(), self.loopAni.height())

        if self.current_mode == "light":
            # 라이트 모드 색상
            gradient.setColorAt((self.gradient_offset + 0.0) % 1.0, QColor("#FFB3B3"))
            gradient.setColorAt((self.gradient_offset + 0.33) % 1.0, QColor("#87CEFA"))
            gradient.setColorAt((self.gradient_offset + 0.66) % 1.0, QColor("#FFB3B3"))
        else:
            # 다크 모드 색상
            gradient.setColorAt((self.gradient_offset + 0.0) % 1.0, QColor("#9B3D3D"))
            gradient.setColorAt((self.gradient_offset + 0.33) % 1.0, QColor("#3B5C91"))
            gradient.setColorAt((self.gradient_offset + 0.66) % 1.0, QColor("#9B3D3D"))

        palette = self.loopAni.palette()
        palette.setBrush(QPalette.Background, QBrush(gradient))
        self.loopAni.setAutoFillBackground(True)
        self.loopAni.setPalette(palette)

        # 루프 애니메이션 모양 설정
    def make_widget_rounded(self, widget, radius=50):
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

        # 위젯 그림자 함수
    def add_shadow_effect(self, object_name,BlurRadius=30):
        target_widget = self.findChild(QWidget, object_name)
        if target_widget:
            shadow_effect = QGraphicsDropShadowEffect(self)
            shadow_effect.setBlurRadius(BlurRadius)  # 그림자 퍼짐 정도 (값이 클수록 더 퍼짐)
            shadow_effect.setXOffset(0)  # X축 이동을 0으로 설정
            shadow_effect.setYOffset(0)  # Y축 이동을 0으로 설정
            shadow_effect.setColor(QColor(0, 0, 0, 180))  # 그림자 색상 (검정색, 투명도 180)
            target_widget.setGraphicsEffect(shadow_effect)

    def slide_in(self): #프로그램 호출 애니메이션
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()

        window_width = self.width()
        window_height = self.height()

        # 애니메이션 시작 위치
        start_x = screen_width+10
        start_y = screen_height - window_height - 25

        # 최종 위치
        end_x = screen_width - window_width
        end_y = screen_height - window_height - 25

        # 애니메이션 설정
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(600)
        self.animation.setStartValue(QRect(start_x, start_y, window_width, window_height))
        self.animation.setEndValue(QRect(end_x, end_y, window_width, window_height))
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.animation.start()

    def slide_out(self): #프로그램 최소화 애니메이션
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()

        window_width = self.width()
        window_height = self.height()

        # 애니메이션 시작 위치
        start_x = screen_width - window_width
        start_y = screen_height - window_height - 25

        # 최종 위치
        end_x = screen_width+10
        end_y = screen_height - window_height - 25

        # 애니메이션 설정
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(500)
        self.animation.setStartValue(QRect(start_x, start_y, window_width, window_height))
        self.animation.setEndValue(QRect(end_x, end_y, window_width, window_height))
        self.animation.setEasingCurve(QEasingCurve.OutCubic)

        # slide_out시 옵션 창이 켜져있으면 옵션 창 닫기
        if self.options_dialog and self.options_dialog.isVisible():
            self.options_dialog.close()
            self.options_dialog = None
        
        self.animation.start()

        # 다크 / 라이트 모드 별 옵션 버튼 icon 변경
    def update_toolbutton_icon(self):
        if self.current_mode == "light":
            self.toolButton.setIcon(QIcon("light_mode_icon.png"))
        else:
            self.toolButton.setIcon(QIcon("dark_mode_icon.png"))

    def apply_external_font(self, widget_name, font_path, font_size=12):
        # 폰트 로드
        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id == -1:
            print(f"폰트를 로드할 수 없습니다: {font_path}")
            return

        # 폰트 패밀리 가져오기
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        font = QFont(font_family, font_size)
        font.setBold(True)

        # 위젯 찾기
        text_edit = self.findChild(QTextEdit, widget_name)
        if text_edit:
            # QTextEdit 기본 글꼴 설정
            text_edit.setFont(font)

            # 커서가 움직이거나 입력될 때 글꼴 유지
            text_edit.textChanged.connect(lambda: self.ensure_font_consistency(text_edit, font))
        else:
            print(f"위젯을 찾을 수 없습니다: {widget_name}")


    def ensure_font_consistency(self, text_edit, font):
        text_edit.blockSignals(True)  # 시그널 차단
        cursor = text_edit.textCursor()
        cursor.select(cursor.Document)  # 전체 텍스트 선택
        format = cursor.charFormat()
        format.setFont(font)  # 지정된 글꼴로 변경
        cursor.setCharFormat(format)
        text_edit.blockSignals(False)  # 시그널 복원


    def ensure_cursor_font(self, text_edit, font):
        cursor = text_edit.textCursor()
        format = cursor.charFormat()
        format.setFont(font)
        cursor.setCharFormat(format)



# 옵션 창 클래스
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

        self.add_shadow_effect("btn1_btn")
        self.add_shadow_effect("btn2_btn")
        self.add_shadow_effect("textEdit")
        self.add_shadow_effect("textEdit_2")
        self.add_shadow_effect("toggle_btn1",3)
        self.add_shadow_effect("toggle_btn2",3)


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
        #else: (mute 기능 함수 호출)

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

    # 위젯 그림자 함수
    def add_shadow_effect(self, object_name,BlurRadius=30):
        target_widget = self.findChild(QWidget, object_name)
        if target_widget:
            shadow_effect = QGraphicsDropShadowEffect(self)
            shadow_effect.setBlurRadius(BlurRadius)  # 그림자 퍼짐 정도 (값이 클수록 더 퍼짐)
            shadow_effect.setXOffset(0)  # X축 이동을 0으로 설정
            shadow_effect.setYOffset(0)  # Y축 이동을 0으로 설정
            shadow_effect.setColor(QColor(0, 0, 0, 180))  # 그림자 색상 (검정색, 투명도 180)
            target_widget.setGraphicsEffect(shadow_effect)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = WindowClass()
    myWindow.show()
    sys.exit(app.exec_())
