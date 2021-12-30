from django.db import models
from django.utils import timezone



class Members(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    username = models.CharField(max_length=100)
    email = models.EmailField(max_length=254)
    phone_number = models.CharField(max_length=30)
    spouse_first_name = models.CharField(max_length=30)
    spouse_last_name = models.CharField(max_length=30)
    spouse_number = models.CharField(max_length=30)
    home_address = models.CharField(max_length=100)

    class Meta:
        unique_together = ('first_name','username',)

    def __str__(self):
        fullname = self.first_name.title() + ' '+ self.last_name.title()
        return fullname.title()

class Member_Request(models.Model):
	mr_date_requested = models.DateTimeField(default=timezone.now)
	mr_amount_requested = models.PositiveBigIntegerField()
	member = models.ForeignKey(Members, on_delete=models.CASCADE)

	def __str__(self):
		object_return1 = self.member
		object_return12 = self.mr_amount_requested
		val1 = str(object_return12)
		val = str(object_return1)
		val2 = val + ' requested  ' + val1
		return val2

class Member_Loan(models.Model):
    date_reviewed = models.DateTimeField(default=timezone.now)
    loan_amount = models.PositiveBigIntegerField()
    member_request = models.ForeignKey(Member_Request, on_delete=models.CASCADE, default=None)

    def __str__(self):
    	object_return1 = self.loan_amount
    	object_return12 = self.member_request
    	b1 = str(object_return1)
    	b = str(object_return12)
    	c = b + ' ' + ' got ' + b1
    	return c


class Member_Repayment(models.Model):
    loan = models.ForeignKey(Member_Loan, on_delete=models.CASCADE)
    amount_repaid = models.PositiveBigIntegerField()
    date_repaid = models.DateTimeField(default=timezone.now)


    def __str__(self):
        a1 = self.loan
        b = str(a1)
        return b

class Unpaid(models.Model):
    loan = models.OneToOneField(Member_Loan, on_delete=models.CASCADE,primary_key=True)
    lb_balance = models.BigIntegerField()
