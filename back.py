import speech_recognition as sr
import keyboard
import os
import subprocess
import threading
import webbrowser
import time
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QMetaObject, Q_ARG
import tkinter as tk
from win import WindowClass
import pyttsx3
from PIL import Image, ImageDraw

current_index = 0

class SpeechRecognitionThread(QThread):
    recognized = pyqtSignal(str)
    terminal_command = pyqtSignal(str)
    ai_response = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.is_recording = False
        self.slide_timer = None
        self.is_speaking = False
        self.current_volume = 1.0
        self.init_engine()

    def init_engine(self):
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 180)
            self.engine.setProperty('volume', self.current_volume)
            voices = self.engine.getProperty('voices')
            for voice in voices:
                if "korean" in voice.name.lower():
                    self.engine.setProperty('voice', voice.id)
                    break
        except Exception as e:
            print(f"TTS 초기화 오류: {e}")

    def stop_and_reinit(self):
        if self.is_speaking:
            try:
                self.engine.stop()
            except:
                pass
            finally:
                self.is_speaking = False
                del self.engine
                self.init_engine()

    def speak_text(self, text):
        try:
            self.is_speaking = True
            self.current_volume = 0.0 if myWindow.is_muted else 1.0
            if hasattr(self, 'engine'):
                del self.engine
            self.init_engine()
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            print(f"TTS 오류: {e}")
            self.init_engine()
        finally:
            self.is_speaking = False
            if not self.is_recording:
                QMetaObject.invokeMethod(myWindow, "slide_out", Qt.QueuedConnection)

    def run(self):
        if self.is_recording:
            return
        if self.slide_timer:
            self.slide_timer.cancel()
            self.slide_timer = None

        self.is_recording = True
        text = recognize_speech()
        self.is_recording = False

        if text:
            self.recognized.emit(text)
            answer = process_command(text, self)
            threading.Thread(target=self.speak_text, args=(answer,)).start()


def recognize_speech():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("녹음중...")
        audio = r.listen(source)
        try:
            _ = r.recognize_google(audio, language='ko-KR')
        except:
            pass
    return "생각 중..."


def process_command(text, thread):
    global current_index

    preset_questions = [
        "남서울대학교 개교일 알려줘",
        "이 컴퓨터의 IP 알려줘",
        "유튜브에서 남서울대학교 검색해봐",
        "바탕화면에 파이썬 코드 만들어봐",
        "유튜브 작동 플로우차트 만들어봐"
    ]

    idx = current_index % len(preset_questions)
    question = preset_questions[idx]
    current_index += 1

    print(f"\n사용자: {question}")

    # 명령별 대기 시간 설정
    delays = [1.2, 2.5, 1.8, 2.0, 3.0]
    wait_time = delays[idx]
    print(f"Vesta가 생각 중...)")
    time.sleep(wait_time)

    if idx == 0:
        answer = "남서울대학교는 1994년 3월 17일에 개교했습니다."
        print(f"Vesta: {answer}")
        thread.ai_response.emit(answer)
        return answer

    elif idx == 1:
        result = subprocess.getoutput("ipconfig")
        QMetaObject.invokeMethod(
            myWindow, "show_command_output", Qt.QueuedConnection,
            Q_ARG(str, "ipconfig"), Q_ARG(str, result)
        )
        answer = "이 컴퓨터의 IP 정보를 확인했습니다."
        thread.ai_response.emit(answer)
        return answer

    elif idx == 2:
        url = "https://www.youtube.com/results?search_query=남서울대학교"
        webbrowser.open(url)
        answer = "유튜브에서 남서울대학교를 검색했습니다."
        thread.ai_response.emit(answer)
        return answer

    elif idx == 3:
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        file_path = os.path.join(desktop, "hello_vesta.py")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("print('Hello, Vesta!')\n")
        answer = "바탕화면에 hello_vesta.py 파일을 생성했습니다."
        thread.ai_response.emit(answer)
        return answer

    else:  # idx == 4
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        img_path = os.path.join(desktop, "youtube_flowchart.png")

        from PIL import Image, ImageDraw, ImageFont
        img = Image.new("RGB", (600, 400), "white")
        draw = ImageDraw.Draw(img)
        steps = ["사용자 입력", "요청 전송", "유튜브 서버", "검색 결과 처리", "화면 표시"]

        try:
            font = ImageFont.truetype("C:/Windows/Fonts/malgun.ttf", 16)
        except Exception:
            font = None

        y = 60
        for step in steps:
            draw.rectangle((200, y-20, 400, y+20), outline="black", fill="#aee")
            draw.text((240, y-10), step, fill="black", font=font)
            if step != steps[-1]:
                draw.line((300, y+20, 300, y+50), fill="black", width=2)
                draw.polygon([(295, y+50), (305, y+50), (300, y+60)], fill="black")
            y += 80
        img.save(img_path)

        answer = "유튜브 작동 플로우차트를 바탕화면에 저장했습니다."
        thread.ai_response.emit(answer)
        return answer


def on_hotkey():
    if recognition_thread.is_speaking:
        recognition_thread.stop_and_reinit()
    if not recognition_thread.is_recording:
        recognition_thread.start()
        QMetaObject.invokeMethod(myWindow, "slide_in", Qt.QueuedConnection)


if __name__ == "__main__":
    app = QApplication([])
    myWindow = WindowClass()
    myWindow.show()
    QMetaObject.invokeMethod(myWindow, "slide_out", Qt.QueuedConnection)

    recognition_thread = SpeechRecognitionThread()
    recognition_thread.recognized.connect(myWindow.update_user_text)
    recognition_thread.terminal_command.connect(myWindow.update_terminal_text)
    recognition_thread.ai_response.connect(myWindow.update_ai_text)

    keyboard.add_hotkey('ctrl+f1+f2', on_hotkey)
    app.aboutToQuit.connect(lambda: recognition_thread.wait())
    app.exec_()
