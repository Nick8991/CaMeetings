from django.shortcuts import render
from django.db import connection
from .models import Outsider



def InsertToDB():
	cursor = connection.cursor()
	cursor.execute('''SELECT nmmrep.id,
    (CURRENT_DATE::Date - date_repaid::Date ) AS numberOfdays,
    SUM(amount_repaid) as pd,
    loan_amount,
    (SUM(amount_repaid) - loan_amount) as dif
    FROM non_members_outsider_loan nmml
    JOIN non_members_outsider_repayment nmmrep
    ON nmml.id = nmmrep.loan_id
    GROUP BY 1,2,4
	''')
	balances = cursor.fetchall()
	my_dict = {}
	for result in balances:
		my_dict['days'] = result[1]
		my_dict['loan_amount'] = result[3]
		my_dict['repay_id'] = result[0]
		my_dict['repaid'] = result[2]
		my_dict['balance'] = result[4]
		loan_month = my_dict['days']//30
		loan_day = my_dict['days']%30

		if loan_month <= 2:
			sub1 = (loan_month*2.5) + ((loan_day/30)*2.5)
			sub2 = my_dict['balance']*(-sub1)
			# total = sub2 - (my_dict['amount_repaid'] + my_dict['balance'])
			if sub2 > my_dict['repaid']:
				rep_id = my_dict['repay_id']
				cursor.execute('''INSERT INTO members_unpaid
					(member_repayment_id, balance) VALUES (%s,%s)
					ON CONFLICT (member_repayment_id) DO NOTHING
					''',[rep_id,sub2])


		else:
			sub1 = (loan_month*10) + ((loan_day/30)*10)
			sub2 = my_dict['loan_amount']*(-sub1)
			if sub2 > my_dict['repaid']:
				rep_id = my_dict['repay_id']
				cursor.execute('''INSERT INTO members_unpaid
					(member_repayment_id, balance) VALUES (%s,%s)
					ON CONFLICT (member_repayment_id) DO NOTHING
					''',[rep_id,sub2])
			else:
				pass


def index1(request):

	member01 = Outsider.objects.all()
	context = {
	'Members':member01
	}
	return render(request,'non_members/outsider.html', context)

def SeekersActiveLoans(request):
	InsertToDB()
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
	ON nmpd.repayment_id = nmmrep.id
	WHERE balance <0
		''')
	results = cursor.fetchall()

	context = {
	'MembersActiveLoans' : results
	}
	return render(request, 'non_members/paidloans.html', context)
