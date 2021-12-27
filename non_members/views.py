from django.shortcuts import render
from django.db import connection
from .models import Outsider



def InsertToDB():
	cursor = connection.cursor()
	cursor.execute('''SELECT nmml.id,
    (CURRENT_DATE::Date - date_reviewed::Date ) AS numberOfdays,
    SUM(amount_repaid) as total_repaid,
    loan_amount
    FROM non_members_outsider_loan nmml
    JOIN non_members_outsider_repayment nmmrep
    ON nmml.id = nmmrep.loan_id
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
			sub1 = (loan_month*0.05) + ((loan_day)*0.05)
			sub2 = float(my_dict['loan_amount'])*(sub1) + my_dict['loan_amount']
			total_debt = sub2 - float(my_dict['total_repaid'])
			rep_id = my_dict['loan_id']
			cursor.execute('''INSERT INTO non_members_unpaid
			(member_loan_id, balance) VALUES (%s,%s)
			ON CONFLICT (member_loan_id) DO UPDATE
			SET balance = EXCLUDED.balance
			''',[rep_id,total_debt])


		elif loan_month > 2:
			sub0 = 2*0.05
			sub1 = ((loan_month-2)*0.1) + ((loan_day/30)*0.1)
			sub2 = ((my_dict['loan_amount']*sub1) + (my_dict['loan_amount']*sub0)) + my_dict['loan_amount']
			total_debt = sub2 - float(my_dict['total_repaid'])
			rep_id = my_dict['loan_id']
			cursor.execute('''INSERT INTO non_members_unpaid
			(member_loan_id, balance) VALUES (%s,%s)
			ON CONFLICT (member_loan_id) DO UPDATE
			SET balance = EXCLUDED.balance
			''',[rep_id,total_debt])


def index1(request):
	InsertToDB()
	member01 = Outsider.objects.all()
	context = {
	'Members':member01
	}
	return render(request,'non_members/outsider.html', context)

def SeekersActiveLoans(request):
	cursor = connection.cursor()
	cursor.execute('''SELECT first_name, last_name, loan_amount, amount_repaid, balance,
	date_reviewed
	FROM non_members_outsider nmm
	JOIN non_members_outsider_request nmmreq
	ON nmm.id = nmmreq.member_id
	JOIN non_members_outsider_loan nmml
	ON nmmreq.id = nmml.outsider_request_id
	JOIN non_members_outsider_repayment nmmrep
	ON nmml.id = nmmrep.loan_id
	JOIN non_members_unpaid nmpd
	ON nmpd.repayment_id = nmmrep.id
	WHERE balance >0
	''')
	results = cursor.fetchall()

	context = {
	'MembersActiveLoans' : results
	}
	return render(request, 'non_members/activeloans.html', context)


def SeekersPaidLoansa(request):
	cursor = connection.cursor()
	cursor.execute('''SELECT first_name, last_name, loan_amount, amount_repaid, balance,
	date_reviewed
	FROM non_members_outsider nmm
	JOIN non_members_outsider_request nmmreq
	ON nmm.id = nmmreq.member_id
	JOIN non_members_outsider_loan nmml
	ON nmmreq.id = nmml.outsider_request_id
	JOIN non_members_outsider_repayment nmmrep
	ON nmml.id = nmmrep.loan_id
	JOIN non_members_unpaid nmpd
	ON nmpd.member_loan_id = nmml.id
	WHERE balance <0
		''')
	results = cursor.fetchall()

	context = {
	'MembersActiveLoans' : results
	}
	return render(request, 'non_members/paidloans.html', context)
