from django.contrib import admin
from django.urls import path
from api_original.views import home

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
]
