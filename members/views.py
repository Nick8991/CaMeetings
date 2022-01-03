from django.shortcuts import render
from django.db import connection
from .models import Members
from . import db

cursor = connection.cursor()



db.load_balance()
db.cal_interest()

def index(request):
	member01 = Members.objects.all()
	context = {
	'Members':member01
	}
	return render(request,'Members/members.html', context)

def MembersActiveLoans(request):
	cursor = connection.cursor()
	cursor.execute('''SELECT INITCAP( CONCAT(first_name,' ',last_name) ) full_name
	,username,loan_amount, 
	SUM(amount_repaid) AS total_paid,u_balance,
	date_reviewed
	FROM members_members mm
	JOIN members_member_request mmreq
	ON mm.id = mmreq.member_id
	JOIN members_member_loan mml
	ON mmreq.id = mml.member_request_id
	JOIN members_member_repayment mmrep
	ON mml.id = mmrep.loan_id
	JOIN members_unpaid mpd
	ON mpd.loan_id = mml.id
	GROUP BY 1,2,3,5,6
	HAVING u_balance >0
	''')
	results = cursor.fetchall()

	context = {
	'MembersActiveLoans' : results
	}
	return render(request, 'Members/activeloans.html', context)


def MembersPaidLoans(request):
	InsertToDB()
	cursor.execute('''SELECT INITCAP( CONCAT(first_name,' ',last_name) ) full_name
	,username,loan_amount, 
	SUM(amount_repaid) AS total_paid,lb_balance,
	date_reviewed
	FROM members_members mm
	JOIN members_member_request mmreq
	ON mm.id = mmreq.member_id
	JOIN members_member_loan mml
	ON mmreq.id = mml.member_request_id
	JOIN members_member_repayment mmrep
	ON mml.id = mmrep.loan_id
	JOIN members_unpaid mpd
	ON mpd.loan_id = mml.id
	GROUP BY 1,2,3,5,6
	HAVING lb_balance <=0

		''')
	results = cursor.fetchall()

	context = {
	'MembersActiveLoans' : results
	}
	return render(request, 'Members/paidloans.html', context)




