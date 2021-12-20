from django.contrib import admin
from .models import Outsider,Outsider_Request, Outsider_Loan, Outsider_Repayment,Unpaid

admin.site.register(Outsider)
admin.site.register(Outsider_Request)
admin.site.register(Outsider_Loan)
admin.site.register(Outsider_Repayment)
admin.site.register(Unpaid)
