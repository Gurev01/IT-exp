# -*- coding: utf-8 -*-

import streamlit as st
import os
import tempfile
from moviepy.editor import VideoFileClip
from pydub import AudioSegment
import requests

# Определение переменной URL здесь
URL = 'https://cloud-api.yandex.net/v1/disk/resources'
TOKEN = 'y0_AgAAAABzb1bkAAuGEAAAAAEAFa0VAACFbd-MVdBPEoGZKpiJ1cW8N56UtA'
headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': f'OAuth {TOKEN}'}

# Определение функции upload_file здесь
def upload_file(loadfile, savefile, replace=False):
    """Загрузка файла.
    savefile: Путь к файлу на Диске
    loadfile: Путь к загружаемому файлу
    replace: true or false Замена файла на Диске"""
    res = requests.get(f'{URL}/upload?path={savefile}&overwrite={replace}', headers=headers).json()
    with open(loadfile, 'rb') as f:
        try:
            requests.put(res['href'], files={'file':f})
        except KeyError:
            print(res)

# Функция для преобразования секунд в минуты и секунды
def convert_seconds_to_minutes(seconds):
    minutes = int(seconds // 60)
    remaining_seconds = int(seconds % 60)
    return minutes, remaining_seconds

# Функции для извлечения аудио из видео и транскрибации аудио
def extract_audio_from_video_with_pydub(video_filepath, output_audio_filepath):
    st.write("Извлечение аудио из видео...")
    video_clip = VideoFileClip(video_filepath)
    temp_audio_filepath = "temp_audio.mp3"
    video_clip.audio.write_audiofile(temp_audio_filepath)

    audio = AudioSegment.from_file(temp_audio_filepath)
    audio = audio.set_channels(1).set_frame_rate(16000)
    audio.export(output_audio_filepath, format="wav", parameters=["-acodec", "pcm_s16le"])
    os.remove(temp_audio_filepath)
    st.write("Аудио успешно извлечено.")



import json
import wave
from vosk import Model, KaldiRecognizer

def convert_seconds_to_minutes(seconds):
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return minutes, seconds

def transcribe_audio(file_path):
    st.write("Транскрибация аудио...")
    model_path = 'model/vosk-model-ru'
    model = Model(model_path)

    wf = wave.open(file_path, "rb")
    rec = KaldiRecognizer(model, wf.getframerate())
    rec.SetWords(True)

    recognition_started = False
    transcription = []
    word_counts = {}
    words_group = [] # Группа слов для которых будет добавлен один таймкод

    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            if not recognition_started:
                st.write("Процесс распознавания...")
                recognition_started = True

    result = rec.FinalResult()
    st.write("Транскрибация завершена.")

    data = json.loads(result)
    words = data['result']

    for word in words:
        text = word['word']
        start_time = word['start']
        end_time = word['end']

        if text not in word_counts:
            word_counts[text] = 1
        else:
            word_counts[text] += 1

        words_group.append(text)
        if len(words_group) == 6: # Если в группе 6 слов, добавляем таймкод
            start_minutes, start_seconds = convert_seconds_to_minutes(start_time)
            transcription.append((start_minutes, start_seconds, " ".join(words_group), word_counts[text]))
            words_group = [] # Сбрасываем группу слов

    # Добавляем оставшиеся слова, если они есть
    if words_group:
        start_minutes, start_seconds = convert_seconds_to_minutes(start_time)
        transcription.append((start_minutes, start_seconds, " ".join(words_group), word_counts[text]))

    # Создание полной транскрибации без времени начала каждого слова
    full_transcription_text = " ".join([text for _, _, text, _ in transcription])

    # Создание транскрибации с таймкодами
    timed_transcription_text = "\n".join([
        f"Время: {start_minutes} мин. {start_seconds} сек. - Слово: {text}"
        for start_minutes, start_seconds, text, count in transcription])

    # Создание краткого пересказа
    # Пример: выбираем первые 10 слов для краткого пересказа
    summary_words = [text for _, _, text, _ in transcription[:10]]
    summary_text = " ".join(summary_words)

    return full_transcription_text, timed_transcription_text, summary_text





# Настройка страницы
st.set_page_config(page_title="Транскрибация текста из видео")

# Заголовок и логотип
st.text("")
st.image(
    "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAfQAAABlCAMAAACMReHqAAAAgVBMVEX///8AAACsrKwhISHW1ta+vr6hoaGSkpLo6Ojb29tqamomJibFxcVHR0ebm5t1dXXOzs5vb2+2trbz8/Pv7++IiIj5+fnh4eFlZWWtra15eXnR0dGDg4McHBy5ubldXV0PDw81NTU8PDxOTk4WFhZFRUUvLy9eXl5VVVU5OTmGhoa20OjhAAAMCklEQVR4nO2d62KqOhCFoWrV1m11q9RabbG2u+15/wc8RZKQrJmQBK2Csn5CuOWDyWQyCVGkqXvTX91V1GLcG0StGqbhKj5U30/nfohWIZrfHYw8U+fvuR+klbd6R0Ge6Ss597O08lP/aMzjOJ2f+2la+eiYzON401JvgF6OyjyO/537gVo5Ndd4fd10HwcVNBwttLOsyTUGu01HafM1k9uTV227tza7one4Cj3BZnmaaq23PhWsu4N62k8F9SHuG5u24JY5Jkh9eYLHCgePDnnKy1BXVcah3a3ZTp7pFXeB16Cg31aEvqB376/egc95Abo7Yl38ked6hB026Dct9HMoISAO0bs4WR+2t9BrpYmoibejnG0kzvYN21voZ9DtQpPRdo+PWxNv4nTQV2+hn14j86l1InKY5UhXkp4ZNOot9NPrr/nUes/sK990rM7rUFxiYm5uoZ9eJdA/oBYPlbgE9IVb6KdXCXTRyxof61LiEi30s+vioP8nT9BCt6q20AcVmGVSLkMF6PdXMuJfW+g/2FFzjMczI0AFNoCeXglQH9UYOhWModyXXq4bUvi69FvQ5zdkPO1w6EOzbAu9on4J+oDSbaHXRr8DPbfDEIZpoddFvwJ9kMYM9SuHnmSqdlSF40r1G9CL3pZBvTnQu0NdPmWKQom2o6uGMnqrXTa2nL4txxP2dIyS3vr1Xtz997JfltUz1y8q35DZy3R3/97ZTbVhtGT+oxnEQIazuVB16HoPW7/TxkBfmkfGM1pkBkXildgB4YWXbNt8bW5cYyIJp94rXiL+tMWOuC938MDUqivi9VAVutmv0gyT2FJ/6JipxQw5fUIR9VRQrVO6KZMz5fApZZDE8Tuft/ZglurRi+avWRI7lFaEPjBvVxurheoRqiH06B/UBfnCSGr4VO6h0PlZYaXP2f1mj8n03WXKU+g4+zCH7swVXVaDDuZNfzaxqQHQSeWAI0WMe1EAoD9Qm6Dq16ryGSYMD4A+wg1xmrdQzgzjcSXowPxG36duqewJawEd87LjO3M3NvraMwH0uzUWVdoyrsJeX9ZDctHXBRhP8Pbjj7yc/WbUc1SADp+IwbxJ0IvkXe6myZzOabEvYHAQswVzJW/OA0kaOUCnb41wM+/JDtBjBejQnpvMGwW9zMATdyjVvtmQEWECL9POfRwaHmLNifLVAWirBEordNlK2vNMYnMjoBMDvyp2kSrWnygoDYB5WL/FACCP3An9masRqo9w6KW2PWoYdJkspqRiKpBKarwPobkfpMPuO6/HjPA4oSd+J+8HQ3cxPzP0judjSGESR0cY+OQddpjZwmHQvxwXtcp8Ghf0rV+xbPZaGPQyvz2X2HMm6PHdA6ep9YKIT3zQZP2dUelRDkFM1ta/ozIMvIum8Pc3rpMOAqE72vNMYte5oNtkjYWjS7VvGCd4+IN5kA16ynvOO+PgZ/ZIDBXl0jt8Luj5G+KMx22SMOhO2x7VFro1GXIOBVPtIYqKgoNY6J/7F2v2l+mNGcM51HPv5/snU7JHz0x3Qc+rnLyvqKyxCYAOzPn1w4w7UKovdBLAWjPGHe0EB724AnWldHaknzgtOoqPJDKrHeiCPrDemqGMtD90d3ueSextDnQSGxuSc67wEKZm9feCxHVSe1XAybE78VLsskD/99q/HS/e5Pvh9OMyMhbok3QLY0R+zBsIHQ38ljSv5BAK3ay/Be7W7DteDU4Nuz+LPRzOj55s9WcC13B7n+sfeHT51s2+5eeh71sGg7qXbY+aCB0HqomoE0igY6OPY6aFGw5PF+N4GlqJYg8D/SUqEQwS6rNWWei5N5BqUQVf5k2E7uhDEePOQMcRcCxQdNWhwafLAoCdKSqSQL8vT9MITJeSHuC7Kuhp26NmQi8NV2+Y1DUCHQuQjpM6CYzd0ZqAqipsBIHuSM0Jgz4hJf2ZNxJ6qYF/Zsoj9CkpgWlQqsqhJ0/BgX0vxmsQumu9mCDoXVLU27ZHDYVeYuDpmngRhU7zm7DbJq8PJiClw+3wgRUrMSL08icKhG4MAWXtegjzhkK3Gnj00HIhdJoMh/6aNI5Ql5vBDAUj10VQDqA7l5EIgm7al3QQYNuj2kJ3pabalsHmw7cInX6v2A+UTbMzYEakYAF0Z2QlrE03H2lj9vcczM8NfTRh5V4Kkx/iZo07gc4shpt0zCKy1Q9fY13VJEB3gcD3y+W9l4TynP9uwFvNVdfx9ELsQIXtdFBBf5giEIGXQRZXTIBK1ThJjHQoELqduvt/Hfwt1R86+w1ynnsmqB8cMM8E8VT5XoRDV180k/deqlDoNupOk9Jg6BEd47IYdy/oMJZWHbqqq1DokPzjMZeNpe7zXx5RtIHQ6Y+LcLFTpUZAD/7SWepe/2ISZZsHnfOrLdMafaBDmy6hk9w7p04JnVL3+/+WKNw86CQrLqZDYFIejhyMjMvAWniX7aTQ8ck82vNMonTjoPN/pbMYeKga5t3AzEoZSgn/KcHpHLm9jFCiJ/OmQreZXW4moU9wBjNeZe4M9gzvpg492CJyv+DI7aWh8l4NXpRvGHSa8lx6QncYFs24/GYSM8iaBtxjKPSqK1EoVv5/ABAHNAy6PcmINfAInSYz4NwZVQK8epur6L7HX4MuYQXMdBOXaBb0Mp+aw4LQaYceU2LVWQBdwP80TgY9pxXypw9xiUZBL80V5/4yh9DfsQCZxKKSKAAF5/hbdDromTfn68PtJS7RKOg0FqeLWRWddGcxEI6ZkQVbdN/54b+le1ECJ3QY0tdDys4U6JltWj0vvhZqDd018kU9eAIdPljrCkU/guG3z4jRmnvVQqHDTeqJHvVbG/bU0AkhnA1GT0rDlaYrRxax0Ahh3jsT89p/o//h1gPNuz5PvoVOVvUaYq4T8dOYGLVupsnCIPpqB6S5J7lWYv0Qx6IEodD1Ay4LeuhU5YhZQ2pBfW8cYuWGo4pGgEx1MFejIHPZVkYDOlSDspBuGQqdtFqFb3ZZ0OMlO1XZmLZs+qXEuGfvDXpbeA/sGORq/7Enf7d0lwGI6R+uJnJevLGaoDlXNhQ6nR3bebh5eXl5GlwadB8Z3y1pfvdZcWigwcBb0g3SP3+23Hbo0bGLDG2Xd9MlTqgyvvVQ6Na1D+4ldGu+QKBkl7fO0PXqIouuiYpAMGaCZOCiBNBqB9yz3q6HQsfczEIS+s51Ck/JmHNDoJOKkfNZ0MCbH2sYdDIIx4/osdKiwKHQo63tpMq8HWndaUl3yG8Wqg10shibelmxZ2WYwjDoNI3aNrxDpX2MwdBJyyWlXM2j/FS5WPHE87ebnE4InSQvaa4TriSiewJB0JmW039UXZtrGgzdul6ouv/j/OdIOkA466+e0KmrY78NozcYAp1dMtI3gUb/doKhWxv14qXDWEAVqYrCZRLrCd1u3Jl71r/YAOjvfBTbK1fu3Wgkg6Fb1yjUYsGH/261eLUwtlhL6AQdvPfYgSoMPBzZ4ddtz7Sxza1BQ8LozfwfeTh0W6dN50En3IZJs1nYVtQROrV+iePcag9AX1nv4sPeaM7oTx1MYfpGOHRbwrUZkro5oGEfas4iSTepI3QSIyHViPFUNVZGFvm3tNHlxrNnNxA/DSQZc60APXpml6eLYNz1a3xTSeutfhby7hwAvTycXh06WfiLmfuL423SwNM/OzwyYbadMxfqtkOP2uuVScisAv3nEsx6htl299rjgaL3A8H/0n8ZQR4Ls+SLrgq3lzezxItjPC4MX0sLxvzDJXrCpGfbRDhDIyaBY3vLOgLsD1s8NFkA9/06N84VwgPFGbXHribHxOFEL8vnIBeadUM15w9kW7aBUeRZluGgZ7Urwpvp12Lk31B2b1dqYK2zXIystTNknsJPyXDyNO6v++PFej0WXZTwDPwyHSuMX2Px0Peau6fC8xoMwlKUDtaj8xcQ/jq851d/lUBvkBK/fw14yNO/aLYuA/pPg4R/samk/nX8tP5SoP/4Cf8d5sann37zWi9AlwP9R7PHUa+inufX8ZHvdVHQW/mphX6FaqFfoVroV6gW+hWqhX6FaqFfoVroV6gW+hWqhX6FaqFfoVroVyiYO/LgPqJV45XsNp1C24DF4Gqh/wHXcruBJGlLyAAAAABJRU5ErkJggg==",
    width=125,
)
st.title("Транскрибация текста из видео")

st.write(
    """  
-   Загрузите видеофайл, извлеките аудио, транскрибируйте его, затем экспортируйте в текстовый файл!
    """
)

st.text("")

c1, c2, c3 = st.columns([1, 4, 1])

with c2:
    with st.form(key="my_form"):
        uploaded_file = st.file_uploader("", type=["mp4", "mkv"])
        st.write(
            f"""
                👆 Загрузите видеофайл.
                """
        )
        submit_button = st.form_submit_button(label="Транскрибировать")

if uploaded_file is not None:
    # Сохранение загруженного файла временно
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mkv") as temp_video:
        temp_video.write(uploaded_file.getvalue())
        temp_video_path = temp_video.name

    # Извлечение аудио из видео
    output_audio_filepath = "files/temp_audio.wav"
    extract_audio_from_video_with_pydub(temp_video_path, output_audio_filepath)
    # Получение полной транскрибации, транскрибации с таймкодами и краткого пересказа
    full_transcription_text, timed_transcription_text, summary_text = transcribe_audio(output_audio_filepath)

    # Транскрибация аудио
    st.write(full_transcription_text) # Corrected line
    st.write("Краткий пересказ:")
    st.write(summary_text)

    # Сохранение текста транскрибации и краткого пересказа в файлы
    # Сохранение текстов в файлы
    with open("files/full_transcription.txt", "w") as f:
        f.write(full_transcription_text)
    with open("files/timed_transcription.txt", "w") as f:
        f.write(timed_transcription_text)
    with open("files/summary.txt", "w") as f:
        f.write(summary_text)

    # Загрузка файлов на Яндекс.Диск
    yandex_disk_folder_path = 'Backup/Transcriptions'  # Пример пути к папке на Яндекс.Диске
    yandex_disk_full_transcription_file_path = f'{yandex_disk_folder_path}/full_transcription.txt'  # Путь к файлу полной транскрибации на Яндекс.Диске
    yandex_disk_timed_transcription_file_path = f'{yandex_disk_folder_path}/timed_transcription.txt'  # Путь к файлу транскрибации с таймкодами на Яндекс.Диске
    yandex_disk_summary_file_path = f'{yandex_disk_folder_path}/summary.txt'  # Путь к файлу краткого пересказа на Яндекс.Диске
    if os.path.exists("files/full_transcription.txt"):
        upload_file('files/full_transcription.txt', yandex_disk_full_transcription_file_path, replace=True)
    else:
        st.error("Файл полной транскрибации не найден.")
    if os.path.exists("files/timed_transcription.txt"):
        upload_file('files/timed_transcription.txt', yandex_disk_timed_transcription_file_path, replace=True)
    else:
        st.error("Файл транскрибации с таймкодами не найден.")
    if os.path.exists("files/summary.txt"):
        upload_file('files/summary.txt', yandex_disk_summary_file_path, replace=True)
    else:
        st.error("Файл краткого пересказа не найден.")

    # Удаление временных файлов
    os.remove(temp_video_path)
    os.remove(output_audio_filepath)
    os.remove("files/full_transcription.txt")
    os.remove("files/timed_transcription.txt")
    os.remove("files/summary.txt")

else:
    st.stop()