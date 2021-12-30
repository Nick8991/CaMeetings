from django.db import models
from django.utils import timezone
from members.models import Members


class Outsider(models.Model):
    id = models.BigAutoField(primary_key=True, serialize=False)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    username = models.CharField(max_length=100)
    email = models.EmailField(max_length=254)
    phone_number = models.CharField(max_length=30)
    spouse_first_name = models.CharField(max_length=30)
    spouse_last_name = models.CharField(max_length=30)
    spouse_number = models.CharField(max_length=30)
    home_address = models.CharField(max_length=100)
    sponsor = models.ForeignKey(Members, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('first_name','username','email')



    def __str__(self):
        fullname = self.first_name.title() +' '+self.last_name.title()
        return fullname


class Outsider_Request(models.Model):
    outsider = models.ForeignKey(Outsider, on_delete=models.CASCADE, default=None)
    date_requested = models.DateTimeField(default=timezone.now)
    amount_requested = models.PositiveBigIntegerField()
    member = models.ForeignKey(Members, on_delete=models.CASCADE)

    def __str__(self):
	    object_return1 = self.outsider
	    object_return12 = self.amount_requested
	    val1 = str(object_return12)
	    val = str(object_return1)
	    val2 = val + ' requested  ' + val1
	    return val2


class Outsider_Loan(models.Model):
    date_reviewed = models.DateTimeField(default=timezone.now)
    loan_amount = models.PositiveBigIntegerField()
    outsider_request = models.ForeignKey(Outsider_Request, on_delete=models.CASCADE)

    def __str__(self):
        a = self.outsider_request
        a1 = str(a)
        b = self.loan_amount
        b1 = str(b)
        c = a1 + ' got '+ b1
        return c


class Outsider_Repayment(models.Model):
    loan = models.ForeignKey(Outsider_Loan, on_delete=models.CASCADE)
    amount_repaid = models.PositiveBigIntegerField()
    date_repaid = models.DateTimeField(default=timezone.now)

    def __str__(self):
        a = self.loan
        return str(a)


class Unpaid(models.Model):
    loan = models.OneToOneField(Outsider_Loan, on_delete=models.CASCADE,primary_key=True)
    lb_balance = models.BigIntegerField()
