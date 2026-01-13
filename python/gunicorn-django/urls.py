from django.urls import path
from app import hello_world

urlpatterns = [
    path('', hello_world, name='hello'),
    path('hello/', hello_world, name='hello_explicit'),
]
