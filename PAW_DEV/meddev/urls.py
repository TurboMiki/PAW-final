from django.urls import path
from . import views

urlpatterns = [
    path('',views.homepage, name='home'),
    path('login_user', views.login_user, name='login_user'),
    path('logout_user',views.logout_user,name='logout_user'),
    path('register_user',views.register_user,name='register_user'),
    path('devices', views.devices, name='devices'),
    path('delete/<int:device_id>/', views.delete_device, name='delete_device'),
    path('borrow/<int:device_id>/', views.borrow_device, name='borrow_device'),
    path('user_devices', views.user_devices, name='user_devices'),
    path('return_device/<int:device_id>/', views.return_device, name='return_device'),
    path('autoclave/<int:device_id>/', views.autoclave_device, name='autoclave_device'),
    path('profile/', views.user_profile, name='user_profile'), 
    path('search/', views.search_results, name='search_results'),
    path('export/csv/', views.export_devices_csv, name='export_devices_csv'),
    path('upload/csv/', views.upload_csv, name='upload_csv'),
]