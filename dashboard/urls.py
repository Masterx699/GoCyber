from django.urls import path
from . import views

urlpatterns= [
    path('', views.home, name='home'),
    path('predict/', views.predict, name='predict'),
    path('api/auth/', views.validasi_key, name='validasi_key'),
    path('access-denied/', views.access_denied, name='access_denied'),
]