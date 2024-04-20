from django.urls import path
from . import views

urlpatterns = [
    
    path('ajax/file/sign/', views.ajax_file_sign, name="ajax_file_sign"),

]