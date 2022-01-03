from django.db import connection


cursor = connection.cursor()

# calculate default loan balance and interest for each loan in the db.
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

		# calculate the duration of each loan base on monthly and daily counts
		loan_month = my_loans['duration']//30
		loan_day = (my_loans['duration']%30)/30

		# loans with less than a two months duration have an interest rate of 2.5 percents.
		if loan_month <= 2:
			sub1 = ((loan_month*0.025) + (loan_day*0.025))/2
			sub2 = (float(my_loans['loan_amount'])*sub1)
			rep_id = my_loans['id']
			cursor.execute('''INSERT INTO members_unpaid
			(loan_id, u_balance,u_interest) VALUES (%s,%s,%s)
			ON CONFLICT (loan_id) DO UPDATE
			SET u_balance = EXCLUDED.u_balance, u_interest = EXCLUDED.u_interest
			''',[rep_id,my_loans['loan_amount'],sub2])

			# loans with more than 2 months duration, pay a 2.5 percent for the first
			# two months and then 10 percent after that.
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
		(CURRENT_DATE::Date - date_repaid::Date ) AS numberOfdays,
		(CURRENT_DATE::Date - date_reviewed::Date ) AS numberOfday
		FROM members_member_repayment mmrep
		JOIN members_member_loan mml
		ON mmrep.loan_id = mml.id
		JOIN members_unpaid mup
		ON mml.id = mup.loan_id
		WHERE mmrep.loan_id = %s
			'''[loan_id])
		repayments = cursor.fetchall()
		my_dict = {}
		for rep in repayments:
			cursor.execute('''SELECT u_balance, u_interest
				FROM members_unpaid mup
				WHERE mup.loan_id = %s
				'''[loan_id])
			loan_amt = cursor.fetchall()

			#my_dict['balance'] = rep[0]
			my_dict['repaid'] = rep[1]
			#my_dict['interest'] = rep[2]
			my_dict['days_repaid'] = rep[3]
			my_dict['days_reviewed'] = rep[4]

			for l in loan_amt:
				my_dict['balance'] = l[0]
				my_dict['interest'] = l[1]

			repaid_months = my_dict['days_repaid']//30
			repaid_days = (my_dict['days_repaid']%30)/30

			#loan_days = (my_dict['days_reviewed']%30)/30
			loan_month = my_dict['days_reviewed']//30

			if (loan_month - repaid_months) <= 2:
				sub1 = ((repaid_months*0.025) + (repaid_days*0.025))
				new_interest = (float(my_dict['balance'])*sub1) + my_dict['interest']

				if my_dict['repaid'] < new_interest:
					latest_interest = new_interest - my_dict['repaid']

					cursor.execute(''' INSERT INTO members_unpaid
						(loan_id,u_interest,u_balance) values
						(%s,%s,%s) ON CONFLICT (loan_id) DO
						UPDATE u_interest = EXCLUDED.u_interest,
						u_balance = EXCLUDED.u_balance
						'''[loan_id, latest_interest, my_dict['balance']])

				elif my_dict['repaid'] > new_interest:
					balance_left = my_dict['repaid'] - new_interest
					latest_interest = 0
					new_balance = my_dict['balance'] - balance_left

					cursor.execute(''' INSERT INTO members_unpaid
						(loan_id,u_interest,u_balance) values
						(%s,%s,%s) ON CONFLICT (loan_id) DO
						UPDATE u_interest = EXCLUDED.u_interest,
						u_balance = EXCLUDED.u_balance
						'''[loan_id, latest_interest, new_balance])

			elif (loan_month - repaid_months) > 2:
				sub1 = ((repaid_months*0.1) + (repaid_days*0.1))
				new_interest = (float(my_dict['balance'])*sub1) + my_dict['interest']

				if my_dict['repaid'] < new_interest:
					latest_interest = new_interest - my_dict['repaid']

					cursor.execute(''' INSERT INTO members_unpaid
						(loan_id,u_interest,u_balance) values
						(%s,%s,%s) ON CONFLICT (loan_id) DO
						UPDATE u_interest = EXCLUDED.u_interest,
						u_balance = EXCLUDED.u_balance
						'''[loan_id, latest_interest, my_dict['balance']])

				elif my_dict['repaid'] > new_interest:
					balance_left = my_dict['repaid'] - new_interest
					latest_interest = 0
					new_balance = my_dict['balance'] - balance_left

					cursor.execute(''' INSERT INTO members_unpaid
						(loan_id,u_interest,u_balance) values
						(%s,%s,%s) ON CONFLICT (loan_id) DO
						UPDATE u_interest = EXCLUDED.u_interest,
						u_balance = EXCLUDED.u_balance
						'''[loan_id, latest_interest, new_balance])



