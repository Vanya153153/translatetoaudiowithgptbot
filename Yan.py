import requests
from peremen import *



def text_to_speech(text):
    # iam_token, folder_id для доступа к Yandex SpeechKit
    iam_token = iam
    folder_id = folder
    # Аутентификация через IAM-токен
    headers = {
        'Authorization': f'Bearer {iam_token}',
    }
    data = {
        'text': text,  # текст, который нужно преобразовать в голосовое сообщение
        'lang': 'ru-RU',  # язык текста - русский
        'voice': 'filipp',  # мужской голос Филиппа
        'folderId': folder_id,
    }
    # Выполняем запрос
    response = requests.post(
        'https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize',
        headers=headers,
        data=data
    )
    if response.status_code == 200:
        return True, response.content  # возвращаем статус и аудио
    else:
        return False, "При запросе в SpeechKit возникла ошибка"
