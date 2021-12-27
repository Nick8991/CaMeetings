from django.urls import path
from . import views

app_name = 'outsiders'
urlpatterns = [
    path('seekers/', views.index1,name ='seekers-home'),
    path('seekers/activeloans', views.SeekersActiveLoans,name ='activeloans'),
    path('seekers/paid-loans', views.SeekersPaidLoansa,name ='paid-loans'),
]
