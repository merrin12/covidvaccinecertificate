from django.contrib import admin
from django.urls import path

from . import views

urlpatterns=[
    path('',views.home,name='home'),
    path('beneficiarylist/',views.beneficiarylist,name='beneficiarylist'),
    path('beneficiarylist/table/',views.table,name='table'),
    path('beneficiarylist/table/certificatedownload/<int:pk>',views.certificatedownload,name='certificatedownload'),

]