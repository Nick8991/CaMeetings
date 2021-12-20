from django.shortcuts import render
from django.db import connection
from .models import Members



def InsertToDB():
	cursor = connection.cursor()
	cursor.execute('''SELECT mmrep.id,
    (CURRENT_DATE::Date - date_reviewed::Date ) AS numberOfdays,
    SUM(amount_repaid) as pd,
    loan_amount,
    (SUM(amount_repaid) - loan_amount) as dif
    FROM members_member_loan mml
    JOIN members_member_repayment mmrep
    ON mml.id = mmrep.loan_id
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
			sub2 = my_dict['balance']*sub1
			# total = sub2 - (my_dict['amount_repaid'] + my_dict['balance'])
			if sub2 > my_dict['repaid']:
				rep_id = my_dict['repay_id']
				cursor.execute('''INSERT INTO members_unpaid
					(member_repayment_id, balance) VALUES (%s,%s)
					ON CONFLICT (member_repayment_id) DO NOTHING
					''',[rep_id,sub2])

		else:
			sub1 = (loan_month*10) + ((loan_day/30)*10)
			sub2 = my_dict['loan_amount']*sub1
			# total = sub2 - (my_dict['repaid'] + my_dict['balance'])
			if sub2 > my_dict['repaid']:
				rep_id = my_dict['repay_id']
				cursor.execute('''INSERT INTO members_unpaid
					(member_repayment_id, balance) VALUES (%s,%s)
					ON CONFLICT (member_repayment_id) DO NOTHING
					''',[rep_id,sub2])

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
	ON mpd.member_repayment_id = mmrep.id
	WHERE balance >0
	''')
	results = cursor.fetchall()

	context = {
	'MembersActiveLoans' : results
	}
	return render(request, 'Members/activeloans.html', context)


def MembersPaidLoans(request):
	cursor = connection.cursor()
	cursor.execute('SELECT first_name, last_name, loan_amount, amount_repaid, balance,mr_date_requested FROM members_members mm JOIN members_member_request mmreq ON mm.id = mmreq.member_id JOIN members_member_loan mml ON mmreq.id = mml.member_request_id JOIN members_member_repayment mmrep ON mml.id = mmrep.loan_id	JOIN members_unpaid mpd ON mpd.member_repayment_id = mmrep.id WHERE balance <0')
	results = cursor.fetchall()

	context = {
	'MembersActiveLoans' : results
	}
	return render(request, 'Members/paidloans.html', context)
