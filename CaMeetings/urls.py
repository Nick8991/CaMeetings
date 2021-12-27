from django.contrib import admin
from django.urls import path, include

admin.site.site_header  =  "InvestmentClub100 Admin Page"  
admin.site.site_title  =  "InvestmentClub100"
admin.site.index_title  =  "InvestmentClub100"
urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('members.urls')),
    path('',include('non_members.urls')),
]
