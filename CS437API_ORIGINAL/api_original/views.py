import json
import os

import requests
from django.shortcuts import render


import api_origin

# Function to fetch news from a specific API
def fetch_news():
    # URL of the API endpoint
    url = 'http://127.0.0.1:5000/APInews?url=https://www.cumhuriyet.com.tr/rss/son_dakika.xml'

    # Sending a GET request to the API
    response = requests.get(url)

    # Check if the response status code is 200 (OK)
    if response.status_code == 200:
        # If the response is OK, parse the JSON and return the 'news' data
        return response.json()['news']
    else:
        # If the response is not OK, return an empty list
        return []

# Function definition for the 'home' view
def home(request):
    # Call the 'fetch_news' function to get news data
    news_list = fetch_news()

    # Render the 'home.html' template
    # Pass the 'news_list' as context to the template
    return render(request, 'api_original/home.html', {'news_list': news_list})

