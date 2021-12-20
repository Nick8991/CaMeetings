from django.urls import path, include
from . import views

app_name = 'members'
urlpatterns = [
    path('members/', views.index,name ='members-home'),
    path('members/activeloans', views.MembersActiveLoans,name ='activeloans'),
    path('members/paid-loans', views.MembersPaidLoans,name ='paid-loans'),
]
