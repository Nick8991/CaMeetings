from django.db import connection


cursor = connection.cursor()

def load_balance():
	cursor.execute('''SELECT loan_amount,
		(CURRENT_DATE::Date - date_reviewed::Date ) AS numberOfdays,
		id
		FROM members_member_loan

		''')
	loans = cursor.fetchall()
	my_loans = {}
	for loan in loans:
		my_loans['loan_amount'] = loan[0]
		my_loans['duration'] = loan[1]
		my_loans['id'] = loan[2]

		loan_month = my_loans['duration']//30
		loan_day = (my_loans['duration']%30)/30

		if loan_month <= 2:
			sub1 = ((loan_month*0.025) + (loan_day*0.025))/2
			sub2 = (float(my_loans['loan_amount'])*sub1)
			rep_id = my_loans['id']
			cursor.execute('''INSERT INTO members_unpaid
			(loan_id, u_balance,u_interest) VALUES (%s,%s,%s)
			ON CONFLICT (loan_id) DO UPDATE
			SET u_balance = EXCLUDED.u_balance, u_interest = EXCLUDED.u_interest
			''',[rep_id,my_loans['loan_amount'],sub2])

		elif loan_month > 2:
			sub0 = 1 * 0.025
			sub1 = ((loan_month-2)*0.1) + ((loan_day/30)*0.1)
			sub2 = float((my_loans['loan_amount']*sub1) + (my_loans['loan_amount']*sub0))
			rep_id = my_loans['loan_id']
			amount = my_loans['loan_amount']
			cursor.execute('''INSERT INTO members_unpaid
			(loan_id, ub_balance,u_interest) VALUES (%s,%s,%s)
			ON CONFLICT (loan_id) DO UPDATE
			SET u_balance = EXCLUDED.u_balance, u_interest = EXCLUDED.u_interest
			''',[rep_id,amount, sub2])



def cal_interest():
	cursor.execute('''SELECT  DISTINCT loan_id
		FROM members_member_repayment mmr
		''')
	loans = cursor.fetchall()
	for loan_ids in loans:
		loan_id = loan_ids[0]
		cursor.execute('''SELECT u_balance, amount_repaid, u_interest,
		CURRENT_DATE::Date - date_repaid::Date ) AS numberOfdays,
		(CURRENT_DATE::Date - date_reviewed::Date ) AS numberOfday	

			''')
		repayments = cursor.fetchall()
		my_dict = {}
		

