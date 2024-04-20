from django.urls import path
from app.views import home as home

urlpatterns = [
    
    path('home/', home.home, name='home'),

]