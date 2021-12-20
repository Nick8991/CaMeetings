from django.contrib import admin
from .models import Member_Request, Member_Loan, Member_Repayment, Members,Unpaid

admin.site.register(Members)
admin.site.register(Member_Request)
admin.site.register(Member_Loan)
admin.site.register(Member_Repayment)
admin.site.register(Unpaid)
