from django.shortcuts import render
from django.db import connection
from .models import Outsider

cursor = connection.cursor()
def default_balance():
	cursor.execute('''SELECT nmol.id, loan_amount
		FROM non_members_outsider_loan nmol
		''')
	loans = cursor.fetchall()
	my_loans = {}
	for loan in loans:
		my_loans['loan_id'] = loan[0]
		my_loans['loan_capital'] = loan[1]
		cursor.execute('''INSERT INTO non_members_unpaid
			(loan_id,lb_balance)
			values (%s,%s,%s) ON CONFLICT (loan_id) 
			DO NOTHING
			''',[my_loans['loan_id'],my_loans['loan_capital']])

def InsertToDB():
	cursor.execute('''SELECT nmol.id,
    (CURRENT_DATE::Date - date_reviewed::Date ) AS numberOfdays,
    SUM(amount_repaid) as pd,
    loan_amount,lb_balance
    FROM non_members_outsider_repayment nmrep
    JOIN non_members_outsider_loan nmol
    ON nmol.id = nmrep.loan_id
    JOIN non_members_unpaid nmu
    ON nmu.loan_id = nmol.id
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
			sub1 = (loan_month*0.05) + ((loan_day)*0.05)
			sub2 = float(my_dict['balance'])*(sub1) + my_dict['loan_amount']
			total_debt = sub2 - float(my_dict['total_repaid'])
			rep_id = my_dict['loan_id']
			cursor.execute('''INSERT INTO non_members_unpaid
			(loan_id, balance) VALUES (%s,%s)
			ON CONFLICT (loan_id) DO UPDATE
			SET balance = EXCLUDED.balance
			''',[rep_id,total_debt])


		elif loan_month > 2:
			sub0 = 2*0.05
			sub1 = ((loan_month-2)*0.1) + ((loan_day/30)*0.1)
			sub2 = ((my_dict['balance']*sub1) + (my_dict['balance']*sub0)) + my_dict['loan_amount']
			total_debt = sub2 - float(my_dict['total_repaid'])
			rep_id = my_dict['loan_id']
			cursor.execute('''INSERT INTO non_members_unpaid
			(loan_id, balance) VALUES (%s,%s)
			ON CONFLICT (loan_id) DO UPDATE
			SET balance = EXCLUDED.balance
			''',[rep_id,total_debt])


def index1(request):
	default_balance()
	InsertToDB()
	InsertToDB()
	member01 = Outsider.objects.all()
	context = {
	'Members':member01
	}
	return render(request,'non_members/outsider.html', context)

def SeekersActiveLoans(request):
	default_balance()
	InsertToDB()
	cursor.execute('''SELECT INITCAP( CONCAT(first_name,' ',last_name) ) full_name, 
	username,loan_amount, SUM(amount_repaid),lb_balance,
	date_reviewed
	FROM non_members_outsider nmm
	JOIN non_members_outsider_request nmmreq
	ON nmm.id = nmmreq.member_id
	JOIN non_members_outsider_loan nmml
	ON nmmreq.id = nmml.outsider_request_id
	JOIN non_members_outsider_repayment nmmrep
	ON nmml.id = nmmrep.loan_id
	JOIN non_members_unpaid nmpd
	ON nmpd.loan_id = nmml.id
	GROUP BY 1,2,3,5,6
	HAVING lb_balance >0
	''')
	results = cursor.fetchall()

	context = {
	'MembersActiveLoans' : results
	}
	return render(request, 'non_members/activeloans.html', context)


def SeekersPaidLoansa(request):
	InsertToDB()
	cursor.execute('''SELECT INITCAP( CONCAT(first_name,' ',last_name) ) full_name, 
	username,loan_amount, SUM(amount_repaid),lb_balance,
	date_reviewed
	FROM non_members_outsider nmm
	JOIN non_members_outsider_request nmmreq
	ON nmm.id = nmmreq.member_id
	JOIN non_members_outsider_loan nmml
	ON nmmreq.id = nmml.outsider_request_id
	JOIN non_members_outsider_repayment nmmrep
	ON nmml.id = nmmrep.loan_id
	JOIN non_members_unpaid nmpd
	ON nmpd.loan_id = nmml.id
	GROUP BY 1,2,3,5,6
	HAVING lb_balance <=0
		''')
	results = cursor.fetchall()

	context = {
	'MembersActiveLoans' : results
	}
	return render(request, 'non_members/paidloans.html', context)
