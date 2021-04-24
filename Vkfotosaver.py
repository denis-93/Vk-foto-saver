import requests
import json
from datetime import datetime
from tqdm import tqdm

with open('vk_token.txt', 'r') as file_object:
    vk_token = file_object.read().strip()
with open('ya_token.txt', 'r') as file_object:
    ya_token = file_object.read().strip()

class VkUser:
    url = 'https://api.vk.com/method/'

    def __init__(self, token, version):
        self.token = vk_token
        self.version = version
        self.params = {
            'access_token': self.token,
            'v': self.version
        }

    def get_profile_photos(self, user_id, count=5):
        profile_photos_url = self.url + 'photos.get'
        profile_photos_params = {
            'owner_id': user_id,
            'album_id': 'profile',
            'extended': 1,
            'photo_sizes': 1,
            'count': count
        }
        res = requests.get(profile_photos_url, params={**self.params, **profile_photos_params})
        res = res.json()['response']['items']
        list_photos = []
        list_name = []
        for item in res:
            dict_photos = {}
            max_width = 0
            photo_url = ''
            photo_type = ''
            if str(item['likes']['count']) + '.jpg' in list_name:
                list_name.append(str(item['likes']['count']) + '-' + datetime.utcfromtimestamp(item['date']).strftime('%Y-%m-%d') + '.jpg')
                dict_photos['file_name'] = str(item['likes']['count']) + '-' + datetime.utcfromtimestamp(item['date']).strftime('%Y-%m-%d') + '.jpg'
            else:
                list_name.append(str(item['likes']['count']) + '.jpg')
                dict_photos['file_name'] = str(item['likes']['count']) + '.jpg'
            for size in item['sizes']:
                if size['width'] > max_width:
                    photo_url = size['url']
                    photo_type = size['type']
            dict_photos['size'] = photo_type
            dict_photos['url'] = photo_url
            list_photos.append(dict_photos)
        return list_photos


class YaUploader:
    def __init__(self, list_photos):
        self.list_photos = list_photos
        self.token = ya_token

    def get_headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': 'OAuth {}'.format(self.token)
        }

    def create_folder(self, name):
        folder_url = 'https://cloud-api.yandex.net/v1/disk/resources'
        headers = self.get_headers()
        params = {'path': '/' + name}
        response = requests.put(folder_url, headers=headers, params=params)
        if response.status_code == 201:
            print(f'Папка {name} создана')
        else:
            print('Ошибка')
        return name

    def upload(self):
        upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
        headers = self.get_headers()
        list_photos = self.list_photos
        name_folder = input('Введите название папки: ')
        self.create_folder(name_folder)
        print(f'Загружаем фотографии в папку {name_folder} на Яндекс.Диск...')
        for photo in tqdm(list_photos):
            params = {'url': photo['url'], 'path': name_folder + '/' + photo['file_name'] }
            href = upload_url
            response = requests.post(href, headers=headers, params=params)
            response.raise_for_status()
        print('Фотографии загружены на Яндекс.Диск.')
        create_json(list_photos)


def create_json(list_photos):
    json_file = []
    for photo in list_photos:
        del photo['url']
        json_file.append(photo)
    with open('info.json', 'w', encoding='utf-8') as f:
        json.dump(json_file, f, ensure_ascii=False, indent=1)
    print('Файл info.json создан.')


vk_client = VkUser(vk_token, '5.130')
photo_list = vk_client.get_profile_photos(552934290)
yadisk = YaUploader(photo_list)
yadisk.upload()





