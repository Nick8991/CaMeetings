from django.shortcuts import render
from django.db import connection
from .models import Outsider
from . import db

cursor = connection.cursor()

db.load_balance()
db.cal_interest()

def index1(request):
	db.load_balance()
	db.cal_interest()
	member01 = Outsider.objects.all()
	context = {
	'Members':member01
	}
	return render(request,'non_members/outsider.html', context)

def SeekersActiveLoans(request):
	db.load_balance()
	db.cal_interest()
	cursor.execute('''SELECT INITCAP( CONCAT(first_name,' ',last_name) ) full_name, 
	username,loan_amount, SUM(amount_repaid),u_balance,
	date_reviewed,u_interest, SUM(r_interest)
	FROM non_members_outsider nmm
	JOIN non_members_outsider_request nmmreq
	ON nmm.id = nmmreq.member_id
	JOIN non_members_outsider_loan nmml
	ON nmmreq.id = nmml.outsider_request_id
	JOIN non_members_outsider_repayment nmmrep
	ON nmml.id = nmmrep.loan_id
	JOIN non_members_unpaid nmpd
	ON nmpd.loan_id = nmml.id
	JOIN non_members_repayment_distribution mrd
	ON mrd.repayment_id = nmmrep.id
	GROUP BY 1,2,3,5,6,7
	HAVING u_balance >0
	''')
	results = cursor.fetchall()

	context = {
	'MembersActiveLoans' : results
	}
	return render(request, 'non_members/activeloans.html', context)


def SeekersPaidLoansa(request):
	db.load_balance()
	db.cal_interest()
	cursor.execute('''SELECT INITCAP( CONCAT(nmm.first_name,' ',nmm.last_name) ) full_name, 
	nmm.username,loan_amount, SUM(amount_repaid),u_balance,
	date_reviewed,SUM(r_interest),mm.username
	FROM non_members_outsider nmm
	JOIN non_members_outsider_request nmmreq
	ON nmm.id = nmmreq.member_id
	JOIN non_members_outsider_loan nmml
	ON nmmreq.id = nmml.outsider_request_id
	JOIN non_members_outsider_repayment nmmrep
	ON nmml.id = nmmrep.loan_id
	JOIN non_members_unpaid nmpd
	ON nmpd.loan_id = nmml.id
	JOIN non_members_repayment_distribution mrd
	ON mrd.repayment_id = nmmrep.id
	JOIN members_members mm
	ON mm.id = nmm.sponsor_id
	GROUP BY 1,2,3,5,6,8
	HAVING u_balance <=0
		''')
	results = cursor.fetchall()

	context = {
	'MembersActiveLoans' : results
	}
	return render(request, 'non_members/paidloans.html', context)
