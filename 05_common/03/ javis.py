import sounddevice as sd
import soundfile as sf
import os
from datetime import datetime
import wave
import json
import csv
from vosk import Model, KaldiRecognizer

DURATION = 5
FS = 44100
BASE_DIR = os.path.dirname(__file__)
RECORDS_DIR = os.path.join(BASE_DIR, 'records')
TEXTS_DIR = os.path.join(BASE_DIR, 'texts')
MODEL_PATH = os.path.join(BASE_DIR, 'model', 'vosk-model-small-ko-0.22')


def record():
    print(f'{DURATION}초 동안 녹음을 시작합니다.')
    recording = sd.rec(int(DURATION * FS), samplerate=FS, channels=1)
    sd.wait()
    print('녹음이 완료되었습니다.')
    return recording


def play(recording):
    print('녹음된 오디오를 재생합니다.')
    sd.play(recording, samplerate=FS)
    sd.wait()
    print('재생이 완료되었습니다.')


def save(recording):
    dt = datetime.now().strftime('%Y%m%d-%H%M%S')
    filename = dt + '.wav'
    filepath = os.path.join(RECORDS_DIR, filename)
    sf.write(filepath, recording, FS, subtype='PCM_16')
    print(f'녹음된 오디오가 파일로 저장되었습니다: {filename}')
    return filepath


def transcribe_audio_files_with_vosk():
    os.makedirs(RECORDS_DIR, exist_ok=True)
    model = Model(MODEL_PATH)

    try:
        wav_files = sorted(f for f in os.listdir(
            RECORDS_DIR) if f.lower().endswith('.wav'))
    except FileNotFoundError:
        print(f'{RECORDS_DIR} 폴더를 찾을 수 없습니다. 먼저 녹음을 진행해주세요.')
        return

    if not wav_files:
        print('텍스트로 변환할 .wav 파일이 없습니다.')
        return

    for wav_file in wav_files:
        audio_filepath = os.path.join(RECORDS_DIR, wav_file)
        with wave.open(audio_filepath, 'rb') as wf:
            sr = wf.getframerate()
            ch = wf.getnchannels()

            recognizer = KaldiRecognizer(model, sr)
            recognizer.SetWords(True)

            print(f'파일 처리중: {wav_file} (sr={sr}, ch={ch})')

            base = os.path.splitext(wav_file)[0]
            csv_path = os.path.join(TEXTS_DIR, base + '.csv')
            with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['음성 파일내에서의 시간', '인식된 텍스트'])

                while True:
                    data = wf.readframes(4000)
                    if not data:
                        break

                    if recognizer.AcceptWaveform(data):
                        res = json.loads(recognizer.Result())
                        for tok in res.get('result', []):
                            start = float(tok.get('start', 0.0))
                            word = (tok.get('word') or '').strip()
                            if word:
                                writer.writerow([f'{start:.2f}', word])

                final = json.loads(recognizer.FinalResult())
                wrote_any = False
                for tok in final.get('result', []):
                    start = float(tok.get('start', 0.0))
                    word = (tok.get('word') or '').strip()
                    if word:
                        writer.writerow([f'{start:.2f}', word])
                        wrote_any = True

                if not wrote_any:
                    text = (final.get('text') or '').strip()
                    if text:
                        writer.writerow(['0.00', text])

            print(f'결과가 {csv_path} 파일에 저장되었습니다.')


def main():
    recording = record()
    if recording is None:
        print('녹음에 실패하였습니다.')
        return
    # play(recording)
    save(recording)
    transcribe_audio_files_with_vosk()


if __name__ == '__main__':
    main()
