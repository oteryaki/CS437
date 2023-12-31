import json
import os

import requests
from django.shortcuts import render


import api_origin

def fetch_news():
    url = 'http://127.0.0.1:5000/APInews?url=https://www.cumhuriyet.com.tr/rss/son_dakika.xml'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()['news']
    else:
        return []

#def fetch_news():
#    file_path = os.path.join(api_origin.settings.BASE_DIR, 'test.json')  # Path to test.json in the project root
#    with open(file_path, 'r') as file:
#        data = json.load(file)
#        return data['news']

def home(request):
    news_list = fetch_news()
    return render(request, 'api_original/home.html', {'news_list': news_list})

