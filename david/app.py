from flask import Flask, request, Response, render_template
import os
from io import BytesIO
from gtts import gTTS
import base64

VALID_LANGUAGES = {'ko', 'en', 'ja', 'es'}
DEFAULT_LANG = 'ko'
app = Flask(__name__, static_folder = 'static')

@app.route("/", methods = ['GET', 'POST'])
def home():
    error_message = None
    audio_data = None
    download_link = None

    if request.method == 'POST':
        text = request.form.get("input_text", "").strip()
        lang = request.form.get("lang", DEFAULT_LANG)

        if not text:
            error_message = "빈 텍스트 입력입니다. 텍스트를 입력해주세요."
        elif lang not in VALID_LANGUAGES:
            error_message = "지원하지 않는 언어입니다. 'ko', 'en', 'ja', 'es' 중에서 선택해주세요."
        else:
            try:
                tts = gTTS(text=text, lang=lang)
                fp = BytesIO()
                tts.write_to_fp(fp)
                fp.seek(0)
                audio_data = base64.b64encode(fp.read()).decode('utf-8')
                audio_data = f"data:audio/mpeg;base64,{audio_base64}"

                # 입력 로그 저장
                with open("input_log.txt", "a", encoding="utf-8") as f:
                    f.write(f"입력: {text}, 언어: ({lang})\n")

            except Exception as e:
                error_message = "TTS 변환에 실패하였습니다."
            
            if audio_data:
                try:
                    log_dir = 'logs'
                    os.makedirs(log_dir, exist_ok=True)
                    log_file_path = os.path.join(log_dir, 'input_log.txt')
                    with open(log_file_path, "a", encoding="utf-8") as f:
                        f.write(f"입력: {text}, 언어: ({lang})\n")
                        
                except Exception as e:
                    print(f"!!! 로그 파일 저장 중 에러 발생: {e}")
    
    return render_template("index.html", error = error_message, audio = audio_data)

    # lang = request.args.get('lang', DEFAULT_LANG)
    #fp = BytesIO()
    #gTTS(text, "com", lang).write_to_fp(fp)

    
    #return Response(fp.getvalue(), mimetype='audio/mpeg') # 페이지 전달없이 바로 재생

if __name__ == '__main__':
    app.run('0.0.0.0', 8080)