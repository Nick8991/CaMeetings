from django.db import connection


cursor = connection.cursor()

# calculate default loan balance and interest for each loan in the db.
def load_balance():
	cursor.execute('''SELECT loan_amount,
		(CURRENT_DATE::Date - date_reviewed::Date ) AS numberOfdays,
		id
		FROM non_members_outsider_loan

		''')
	loans = cursor.fetchall()
	my_loans = {}
	for loan in loans:
		my_loans['loan_amount'] = loan[0]
		my_loans['duration'] = loan[1]
		my_loans['id'] = loan[2]

		# calculate the duration of each loan base on monthly and daily counts
		loan_month = my_loans['duration']//30
		loan_day = (my_loans['duration']%30)/30

		# loans with less than a two months duration have an interest rate of 2.5 percents.
		if loan_month <= 2:
			sub1 = ((loan_month*0.05) + (loan_day*0.05))/2
			sub2 = (float(my_loans['loan_amount'])*sub1)
			rep_id = my_loans['id']
			cursor.execute('''INSERT INTO non_members_unpaid
			(loan_id, u_balance,u_interest) VALUES (%s,%s,%s)
			ON CONFLICT (loan_id) DO UPDATE
			SET u_balance = EXCLUDED.u_balance, u_interest = EXCLUDED.u_interest
			''',[rep_id,my_loans['loan_amount'],sub2])

			# loans with more than 2 months duration, pay a 2.5 percent for the first
			# two months and then 10 percent after that.
		elif loan_month > 2:
			sub0 = 1 * 0.05
			sub1 = ((loan_month-2)*0.1) + ((loan_day/30)*0.1)
			sub2 = float((my_loans['loan_amount']*sub1) + (my_loans['loan_amount']*sub0))
			rep_id = my_loans['id']
			amount = my_loans['loan_amount']
			cursor.execute('''INSERT INTO non_members_unpaid
			(loan_id, u_balance,u_interest) VALUES (%s,%s,%s)
			ON CONFLICT (loan_id) DO UPDATE
			SET u_balance = EXCLUDED.u_balance, u_interest = EXCLUDED.u_interest
			''',[rep_id,amount, sub2])



def cal_interest():
	cursor.execute('''SELECT  DISTINCT loan_id
		FROM non_members_outsider_repayment mmr''')
	loans = cursor.fetchall()
	for loan_ids in loans:
		loan_id = loan_ids[0]

		cursor.execute('''SELECT u_balance, amount_repaid, u_interest,
		(CURRENT_DATE::Date - date_reviewed::Date) AS numberOfday,mmrep.id
		FROM non_members_outsider_repayment mmrep
		JOIN non_members_outsider_loan mml
		ON mmrep.loan_id = mml.id
		JOIN non_members_unpaid mup
		ON mml.id = mup.loan_id
		WHERE mmrep.loan_id = %s AND u_balance > 0
			''',[loan_id])
		repayments = cursor.fetchall()
		my_dict = {}
		for rep in repayments:
			cursor.execute('''SELECT u_balance, u_interest
				FROM non_members_unpaid mup
				WHERE mup.loan_id = %s
				''',[loan_id])
			loan_amt = cursor.fetchall()

			my_dict['repaid'] = rep[1]
			my_dict['days_reviewed'] = rep[3]
			my_dict['repayment_id'] = rep[4]

			for l in loan_amt:
				my_dict['balance'] = l[0]
				my_dict['interest'] = l[1]

			new_interest = my_dict['interest']


			if my_dict['repaid'] < new_interest:
				latest_interest = new_interest - my_dict['repaid']

				paid_interest = my_dict['repaid']
				paid_balance = 0

				cursor.execute(''' INSERT INTO non_members_repayment_distribution
					(repayment_id,r_balance, r_interest, loan_id) values 
					(%s,%s,%s,%s) ON CONFLICT (repayment_id)
					DO UPDATE SET r_balance = EXCLUDED.r_balance,
					r_interest = EXCLUDED.r_interest
					''', [my_dict['repayment_id'],paid_balance,paid_interest,loan_id])

				cursor.execute(''' INSERT INTO non_members_unpaid
					(loan_id,u_interest,u_balance) values
					(%s,%s,%s) ON CONFLICT (loan_id) DO UPDATE
					SET u_interest = EXCLUDED.u_interest,
					u_balance = EXCLUDED.u_balance
					''',[loan_id, latest_interest, my_dict['balance']])

			elif my_dict['repaid'] > new_interest:
				balance_left = my_dict['repaid'] - new_interest
				latest_interest = 0
				new_balance = my_dict['balance'] - balance_left

				paid_interest = new_interest
				paid_balance = balance_left

				cursor.execute(''' INSERT INTO non_members_repayment_distribution
					(repayment_id,r_balance, r_interest, loan_id) values 
					(%s,%s,%s,%s) ON CONFLICT (repayment_id)
					DO UPDATE SET r_balance = EXCLUDED.r_balance,
					r_interest = EXCLUDED.r_interest

					''', [my_dict['repayment_id'],paid_balance,paid_interest,loan_id]) 

				cursor.execute(''' INSERT INTO non_members_unpaid
					(loan_id,u_interest,u_balance) values
					(%s,%s,%s) ON CONFLICT (loan_id) DO UPDATE
					SET u_interest = EXCLUDED.u_interest,
					u_balance = EXCLUDED.u_balance
					''',[loan_id, latest_interest, new_balance])




