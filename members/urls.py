from django.urls import path
from . import views

urlpatterns = [
    path('members/', views.index,name ='members-home'),
    path('members/activeloans', views.MembersActiveLoans,name ='activeloans'),
    path('members/paid-loans', views.MembersPaidLoans,name ='paid-loans'),
]
