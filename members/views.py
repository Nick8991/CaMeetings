from django.shortcuts import render
from django.db import connection
from .models import Members

cursor = connection.cursor()

def default_balance():
	cursor.execute('''SELECT mmml.id, loan_amount
		FROM members_member_loan mml
		ORDER BY 1 DESC
		''')
	loans = cursor.fetchall()
	my_loans = {}
	for loan in loans:
		my_loans['loan_id'] = loan[0]
		my_loans['loan_capital'] = loan[1]
		cursor.execute('''INSERT INTO members_member_loan
			(loan_id,interest,lb_balance)
			values (%s,%s,%s) ON CONFLICT (loan_id) 
			DO NOTHING
			''',[my_loans['loan_id'],0,my_loans['loan_capital']])





def InsertToDB():
	cursor.execute('''SELECT mml.id,
    (CURRENT_DATE::Date - date_reviewed::Date ) AS numberOfdays,
    SUM(amount_repaid) as pd,
    loan_amount
    FROM members_member_loan mml
    JOIN members_member_repayment mmrep
    ON mml.id = mmrep.loan_id
    GROUP BY 1,2,4
	''')
	balances = cursor.fetchall()
	my_dict = {}
	for result in balances:
		my_dict['loan_id'] = result[0]
		my_dict['days'] = result[1]
		my_dict['total_repaid'] = result[2]
		my_dict['loan_amount'] = result[3]
		loan_month = my_dict['days']//30
		loan_day = (my_dict['days']%30)/30

		if loan_month <= 2:
			sub1 = (loan_month*0.025) + (loan_day*0.025)
			sub2 = (float(my_dict['loan_amount'])*sub1) + my_dict['loan_amount']
			total_debt = sub2 - float(my_dict['total_repaid'])
			rep_id = my_dict['loan_id']
			cursor.execute('''INSERT INTO members_unpaid
			(member_loan_id, balance) VALUES (%s,%s)
			ON CONFLICT (member_loan_id) DO UPDATE
			SET balance = EXCLUDED.balance
			''',[rep_id,total_debt])

		elif loan_month > 2:
			sub0 = 2 * 0.025
			sub1 = ((loan_month-2)*0.1) + ((loan_day/30)*0.1)
			sub2 = float((my_dict['loan_amount']*sub1) + (my_dict['loan_amount']*sub0)) + (my_dict['loan_amount'])
			total_debt = sub2 - float(my_dict['total_repaid'])
			rep_id = my_dict['loan_id']
			cursor.execute('''INSERT INTO members_unpaid
			(member_loan_id, balance) VALUES (%s,%s)
			ON CONFLICT (member_loan_id) DO UPDATE
			SET balance = EXCLUDED.balance
			''',[rep_id,total_debt])

def index(request):

	member01 = Members.objects.all()
	context = {
	'Members':member01
	}
	return render(request,'Members/members.html', context)

def MembersActiveLoans(request):
	InsertToDB()
	cursor = connection.cursor()
	cursor.execute('''SELECT first_name, last_name, loan_amount, amount_repaid, balance,
	date_reviewed
	FROM members_members mm
	JOIN members_member_request mmreq
	ON mm.id = mmreq.member_id
	JOIN members_member_loan mml
	ON mmreq.id = mml.member_request_id
	JOIN members_member_repayment mmrep
	ON mml.id = mmrep.loan_id
	JOIN members_unpaid mpd
	ON mpd.member_loan_id = mml.id
	WHERE balance >0
	''')
	results = cursor.fetchall()

	context = {
	'MembersActiveLoans' : results
	}
	return render(request, 'Members/activeloans.html', context)


def MembersPaidLoans(request):
	cursor = connection.cursor()
	cursor.execute('''SELECT first_name, last_name, loan_amount,
	amount_repaid, balance,mr_date_requested FROM members_members mm
	JOIN members_member_request mmreq ON mm.id = mmreq.member_id JOIN 
	members_member_loan mml ON mmreq.id = mml.member_request_id 
	JOIN members_member_repayment mmrep ON mml.id = mmrep.loan_id	
	JOIN members_unpaid mpd ON mpd.member_loan_id = mml.id WHERE balance <0''')
	results = cursor.fetchall()

	context = {
	'MembersActiveLoans' : results
	}
	return render(request, 'Members/paidloans.html', context)




