## 반달곰 커피 홈페이지 

[https://반달곰 커피](https://반달곰%20커피)

오디오 출력 소스코드


```python
lang = request.args.get('lang', DEFAULT_LANG)
fp = BytesIO()
gTTS(text, "com", lang).write_to_fp(fp)
encoded_audio_data = base64.b64encode(fp.getvalue())
```

![반달곰 커피 대표 이미지](david.jpg)