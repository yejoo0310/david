from flask import Flask, request, Response, render_template
import os # os 디렉토리 경로 생성 및 파일을 관리하기 위해
from io import BytesIO # 메모리에서 파일처럼 데이터를 다루기 위해 
from gtts import gTTS # 텍스트를 음성으로 변환
import base64 # 바이너리 데이터를 인코딩해 웹에서 오디오 들을 수 있게 함

VALID_LANGUAGES = {'ko', 'en', 'ja', 'es'}
DEFAULT_LANG = 'ko'

class InvalidInputError(Exception):
    pass

app = Flask(__name__, static_folder = 'static')

@app.route("/", methods = ['GET', 'POST'])
def home():
    error_message = None
    audio_data = None

    if request.method == 'POST':
        text = request.form.get("input_text", "").strip()
        lang = request.form.get("lang", "").strip() or DEFAULT_LANG
        
        try:
            if not text:
                raise InvalidInputError("빈 텍스트 입력입니다. 텍스트를 입력해주세요.")
            if lang not in VALID_LANGUAGES:
                raise InvalidInputError("지원하지 않는 언어입니다. 'ko', 'en', 'ja', 'es' 중에서 선택해주세요.")

            # gTTS 로 텍스트를 음성으로 변환
            tts = gTTS(text=text, lang=lang)
            fp = BytesIO() # 파일 저장 없이 메모리에 저장 (파일처럼 동작하는 메모리 공간)
            tts.write_to_fp(fp)
            fp.seek(0)
            audio_base64 = base64.b64encode(fp.read()).decode('utf-8')
            # 브라우저에서 바로 재생 가능한 data URL 포맷 만듦
            audio_data = f"data:audio/mpeg;base64,{audio_base64}"

            # 입력 로그 저장
            os.makedirs("logs", exist_ok=True)
            with open(os.path.join("logs", "input_log.txt"), "a", encoding="utf-8") as f:
                f.write(f"입력: {text}, 언어: {lang}\n")

        except InvalidInputError as e:
            error_message = str(e)

        except Exception as e:
            error_message = "TTS 변환에 실패하였습니다."
    
    return render_template("index.html", error = error_message, audio = audio_data)

if __name__ == '__main__':
    app.run('0.0.0.0', 8080)