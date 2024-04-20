from django.urls import path
from api.views import location_ping_views as views

urlpatterns = [

    path('', views.get_location_pings, name="api_location_pings"),
    path('add/', views.add_location_ping, name="api_add_location_ping"),
    path('add/bulk/', views.add_location_pings, name="api_add_location_pings"),
    path('update/bulk/', views.update_location_pings, name="api_update_location_pings"),
    path('archive/bulk/', views.archive_location_pings, name="api_archive_location_pings"),
    path('<str:location_ping_id>/', views.get_location_ping, name="api_location_ping"),
    path('<str:location_ping_id>/update/', views.update_location_ping, name="api_update_location_ping"),
    path('<str:location_ping_id>/archive/', views.archive_location_ping, name="api_archive_location_ping"),
    
]