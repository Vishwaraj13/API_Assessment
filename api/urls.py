
from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [
    path('transaction/', views.transaction,name='transaction'),
    path('get_details/', views.get_details,name='get_details'),

]