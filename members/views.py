from django.shortcuts import render
from django.db import connection
from .models import Members
from . import db

cursor = connection.cursor()



db.load_balance()


def InsertToDB():
	cursor.execute('''SELECT mml.id,
    (CURRENT_DATE::Date - date_reviewed::Date ) AS numberOfdays,
    SUM(amount_repaid) as pd,
    loan_amount,u_balance
    FROM members_member_repayment mmrep
    JOIN members_member_loan mml
    ON mml.id = mmrep.loan_id
    JOIN members_unpaid mu
    ON mu.loan_id = mml.id
    GROUP BY 1,2,4,5
	''')
	balances = cursor.fetchall()
	my_dict = {}
	for result in balances: 
		my_dict['loan_id'] = result[0]
		my_dict['days'] = result[1]
		my_dict['total_repaid'] = result[2]
		my_dict['loan_amount'] = result[3]
		my_dict['balance'] = result[4]

		loan_month = my_dict['days']//30
		loan_day = (my_dict['days']%30)/30

		if loan_month <= 2:
			sub1 = (loan_month*0.025) + (loan_day*0.025)
			sub2 = (float(my_dict['balance'])*sub1) + my_dict['loan_amount']
			total_debt = sub2 - float(my_dict['total_repaid'])
			rep_id = my_dict['loan_id']
			cursor.execute('''INSERT INTO members_unpaid
			(loan_id, lb_balance) VALUES (%s,%s)
			ON CONFLICT (loan_id) DO UPDATE
			SET lb_balance = EXCLUDED.lb_balance
			''',[rep_id,total_debt])

		elif loan_month > 2:
			sub0 = 2 * 0.025
			sub1 = ((loan_month-2)*0.1) + ((loan_day/30)*0.1)
			sub2 = float((my_dict['balance']*sub1) + (my_dict['balance']*sub0)) + (my_dict['loan_amount'])
			total_debt = sub2 - float(my_dict['total_repaid'])
			rep_id = my_dict['loan_id']
			cursor.execute('''INSERT INTO members_unpaid
			(loan_id, lb_balance) VALUES (%s,%s)
			ON CONFLICT (member_loan_id) DO UPDATE
			SET lb_balance = EXCLUDED.lb_balance
			''',[rep_id,total_debt])

def index(request):
	db.load_balance()
	#InsertToDB()
	member01 = Members.objects.all()
	context = {
	'Members':member01
	}
	return render(request,'Members/members.html', context)

def MembersActiveLoans(request):
	InsertToDB()
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




