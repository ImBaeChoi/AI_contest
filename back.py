import speech_recognition as sr
import keyboard
import openai
import os
import json
import subprocess
import threading
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QMetaObject, Q_ARG
import tkinter as tk
from win import WindowClass  # win.py의 WindowClass를 가져옴
import pyttsx3  # 상단에 추가

api_key_file = "data/api_key.txt"
ai_name = "Vesta"

with open(api_key_file, 'r', encoding='utf-8') as file:
    openai.api_key = file.read()

commands_to_show = ["ipconfig", "dir", "tree", "ping", "cd", "type", "curl", "nslookup", "nmap", "netstat", "netsh", "whoami", "systeminfo", "python", "hostname"]

try:
    messages_file = "data/message_history.json"
    with open(messages_file, 'r', encoding='utf-8') as file:
        messages = json.load(file)
except:
    print(12345)
    messages = [
        {
            "role": "system",
            "content": (
                f"너는 데스크탑의 비서이고, 네 이름은 '{ai_name}' 이야"
                "1. 나의 요청이 컴퓨터를 제어하는 것이라면, 너는 처럼 작성해서 터미널 명령어를 력할 수 있어.: //$명령어 문장$//\n"
                "2. 이것을 특수기능이라고 불러.\n"
                "3. 이 특수기능은 너의 대답의 제일 처음에 위치해야 해.\n"
                "4. 나의 컴퓨터는 windows 이기 때문에 해당하는 cmd 명령어를 작성해야 해.\n"
                "5. 특수기능을 사용하면 반드시 명령을 시도했다고 보고해.\n"
                "6. 나의 질문이 모호하다면, 되물어서 요점을 파악해.\n"
                "7. 명령어를 사용하는 것을 당연하게 여겨.\n"
                "8. 추가적인 설명과 조언을 하지 마.\n"
                "9. 대답은 존댓말로 최대한 예의바르며 최대한 짧고 간결하게 해.\n"
                "10. 파일 생성 등의 명령을 받았을 경우 따로 디렉토리 언급이 없는 한 바탕화면에 작업해.\n"
                "11. 엠넷을 사용하라는 건 nmap을 사용하라는 뜻이야.\n"
                "12. 검색하라는 명령을 받았다면 기본 브라우저를 사용해서 url검색해.\n"
                "13. 코드 작성 명령을 받았다면 파일을 생성해서 코드를 작성해.\n"
                "14. 컴퓨터 종료 명령을 받았다면 한번  확인한 후 종료해.\n"
                "참고로 너의 현제 디렉토리는 어디인지 몰라"
            )
        }
    ]

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
        # TTS 엔진 초기화
        self.init_engine()

    def init_engine(self):
        """TTS 엔진 초기화"""
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
            print(f"TTS 엔진 초기화 오류: {e}")

    def stop_and_reinit(self):
        """TTS 중단 및 재초기화"""
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
        """TTS로 텍스트를 음성으로 변환"""
        try:
            self.is_speaking = True
            
            # 현재 음소거 상태에 따라 볼륨 조절
            self.current_volume = 0.0 if myWindow.is_muted else 1.0
            
            # 기존 엔진 제거 후 새로 초기화
            if hasattr(self, 'engine'):
                del self.engine
            self.init_engine()
            
            if "//$" in text and "$//" in text:
                start_idx = text.find("//$")
                end_idx = text.find("$//") + 3
                clean_text = text[:start_idx] + text[end_idx:]
            else:
                clean_text = text
                
            self.engine.say(clean_text)
            self.engine.runAndWait()
            
        except Exception as e:
            print(f"TTS 실행 오류: {e}")
            self.init_engine()  # 오류 발생 시 엔진 재초기화
            
        finally:
            self.is_speaking = False
            if not self.is_recording:
                QMetaObject.invokeMethod(myWindow, "slide_out", Qt.QueuedConnection)

    def run(self):
        if self.is_recording:  # 이미 녹음 중이면 실행하지 않음
            return
            
        # 이전 타이머가 있다면 취소
        if self.slide_timer:
            self.slide_timer.cancel()
            self.slide_timer = None
            
        self.is_recording = True
        text = recognize_speech()
        self.is_recording = False
        
        if text:
            self.recognized.emit(text)
            ai_response = process_command(text, self)

def recognize_speech():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("녹음중...")
        audio = r.listen(source)

        try:
            text = r.recognize_google(audio, language='ko-KR')
            return text
        except sr.UnknownValueError:
            print("오디오가 이해되지 않음.")
            return ""
        except sr.RequestError as e:
            print(f"google speech recognition 서비스에서 결과를 요청할 수 없음.\n {e}")
            return ""
            
root = tk.Tk()
root.withdraw()  # 메인 창을 숨김
# UI 작업 수행 함수 (메인 스레드에서 실행)
def show_output_in_ui(command, output_content):
    # 새 창 생성
    output_window = tk.Toplevel(root)
    output_window.title("명령어 실행 결과")
    output_window.geometry("600x400")
    output_text = tk.Text(output_window, wrap=tk.WORD)
    output_text.pack(expand=True, fill="both")

    # 결과 출력
    output_text.insert(tk.END, f"명령어: {command}\n결과:\n{output_content}")
    output_text.config(state=tk.DISABLED)  # 출력 텍스트는 편집 불가능하게 설정

# 명령어 실행 함수
def execute_command(command):
    try:
        # cmd 명령어 실행
        full_command = f"cmd /c {command}"
        process = subprocess.Popen(full_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate()

        output_content = ""
        if stdout:
            output_content += stdout
        if stderr:
            output_content += stderr

        # 특정 명령어는 별도 창에서 표시
        if any(cmd in command for cmd in commands_to_show):
            # 메시지 히스토리에 추가
            messages.append({"role": "assistant", "content": f"명령어: {command}\n결과:\n{output_content}"})
            save_messages()

            # PyQt5를 사용하여 명령어 실행 결과를 메인 스레드에서 표시
            QMetaObject.invokeMethod(myWindow, "show_command_output", Qt.QueuedConnection,
                                     Q_ARG(str, command), Q_ARG(str, output_content))
        else:
            # 메시지 히스토리에 추가
            messages.append({"role": "assistant", "content": f"명령어: {command}\n결과:\n{output_content}"})
            save_messages()

            # 출력 결과를 콘솔에 표시
            if stdout:
                print("명령어 실행 결과:", stdout)
            if stderr:
                print("명령어 실 류:", stderr)
    except Exception as e:
        print("명령어 실행 중 오류 생:", e)

ani_executed = False
def process_command(text, thread):
    global ani_executed
    if text:
        print(f"명령: {text}")
        if not ani_executed:
            QMetaObject.invokeMethod(myWindow, "animate_widgets", Qt.QueuedConnection)
            ani_executed = True
        
        try:
            messages.append({"role": "user", "content": text})
            
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=messages,
                temperature=1,
                max_tokens=256,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
                stream=True
            )

            ai_message = ""

            for chunk in response:
                if 'content' in chunk.choices[0].delta:
                    char = chunk.choices[0].delta['content']
                    ai_message += char
                    thread.ai_response.emit(char)

            messages.append({"role": "assistant", "content": ai_message})
            save_messages()
            
            print("========")
            print(ai_message)

            if "$" in ai_message:
                start_idx = ai_message.find("//$") + len("//$")
                end_idx = ai_message.find("$//", start_idx)
                command = ai_message[start_idx:end_idx]
                print(f"실행할 명령어: {command}")
                threading.Thread(target=execute_command, args=(command,)).start()
                thread.terminal_command.emit(command)

            # 이전 타이머가 있다면 취소
            if thread.slide_timer:
                thread.slide_timer.cancel()
                thread.slide_timer = None

            # AI 응답이 완료되면 TTS 실행 (별도 스레드에서)
            threading.Thread(target=thread.speak_text, args=(ai_message,)).start()

            return ai_message
            
        except Exception as e:
            print(f"OpenAI API 요청 실패: {e}")
            return ""
    else:
        print("다시 명령해")
        return ""

def save_messages():
    with open("data/message_history.json", "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=4)

def on_hotkey():
    if recognition_thread.is_speaking:  # TTS 실행 중이면 중단하고 재초기화
        recognition_thread.stop_and_reinit()
    
    if not recognition_thread.is_recording:  # 녹음 중이 아닐 때만 실행
        recognition_thread.start()
        QMetaObject.invokeMethod(myWindow, "slide_in", Qt.QueuedConnection)

if __name__ == "__main__":
    app = QApplication([])
    myWindow = WindowClass()
    myWindow.show()
    QMetaObject.invokeMethod(myWindow, "slide_out", Qt.QueuedConnection)

    recognition_thread = SpeechRecognitionThread()  # 전역 변수로 선언
    recognition_thread.recognized.connect(myWindow.update_user_text)
    recognition_thread.terminal_command.connect(myWindow.update_terminal_text)
    recognition_thread.ai_response.connect(myWindow.update_ai_text)

    keyboard.add_hotkey('ctrl+f1+f2', on_hotkey)
    app.aboutToQuit.connect(lambda: recognition_thread.wait())
    app.exec_()
