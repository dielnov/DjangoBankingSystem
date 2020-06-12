from bank.generator import transID, getMyDate
from bank.models import AccountDetail, CorporateAccount, IndividualAccount
import csv
import os
from django.contrib.staticfiles.storage import staticfiles_storage

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
log_dir = os.path.join(BASE_DIR, 'accounts/logs/')


def transact(senderAcc, receiverAcc, amount):

    # Get Sender & Receiver
    sender = AccountDetail.objects.get(accnum=senderAcc)
    try:
        receiver = AccountDetail.objects.get(accnum=receiverAcc)
    except:
        return 'Account Number Does Not Exist!'

    # Common Details To Collect
    date_of_transaction = getMyDate()
    transactionID = transID()
    transactionAmount = amount

    # Sender Details To Collect
    sender_balance = sender.balance
    sender_acc_num = senderAcc
    if sender.account.isCorporate:
        sender_legal_name = CorporateAccount.objects.get(
            account=sender.account)
    else:
        sender_legal_name = IndividualAccount.objects.get(
            account=sender.account)

    # Receiver Details To Collect
    receiver_balance = receiver.balance
    receiver_acc_num = receiverAcc
    if receiver.account.isCorporate:
        receiver_legal_name = CorporateAccount.objects.get(
            account=receiver.account)
    else:
        receiver_legal_name = IndividualAccount.objects.get(
            account=receiver.account)

    # Read Balance From Sender CSV
    with open(staticfiles_storage.path('logs/' + senderAcc + '.csv'), 'r', newline='') as new_file:
        csvReader = csv.reader(new_file, delimiter='\t')
        rows = list(csvReader)
        total_rows = len(rows)
        counter = 0
        for row in rows:
            if counter == total_rows-1:
                sender_balance = rows[total_rows-1][-1]
            counter += 1

    new_balance = float(sender_balance) - float(amount)
    if new_balance < 0:
        return 'Insufficient funds. Balance is ' + sender_balance

    # Write Transaction To Sender CSV
    with open(staticfiles_storage.path('logs/' + senderAcc + '.csv'), 'a', newline='') as new_file:
        fieldnames = ['TransactionsID', 'Date',
                      'Creditor', 'Debtor', 'Amount', 'Balance']
        csv_writer = csv.DictWriter(
            new_file, fieldnames=fieldnames, delimiter='\t')
        csv_writer.writerow({'TransactionsID': transactionID, 'Date': date_of_transaction,
                             'Creditor': sender_legal_name, 'Debtor': receiver_legal_name, 'Amount': amount, 'Balance': str(new_balance)})
        sender.balance = str(new_balance)
        sender.save()

    # Read Balance From Receiver CSV
    with open(staticfiles_storage.path('logs/' + receiverAcc + '.csv'), 'r', newline='') as new_file:
        csvReader = csv.reader(new_file, delimiter='\t')
        rows = list(csvReader)
        total_rows = len(rows)
        counter = 0
        for row in rows:
            if counter == total_rows-1:
                receiver_balance = rows[total_rows-1][-1]
            counter += 1

    new_balance = float(receiver_balance) + float(amount)

    # Write Transaction To Receiver CSV
    with open(staticfiles_storage.path('logs/' + receiverAcc + '.csv'), 'a', newline='') as new_file:
        fieldnames = ['TransactionsID', 'Date',
                      'Creditor', 'Debtor', 'Amount', 'Balance']
        csv_writer = csv.DictWriter(
            new_file, fieldnames=fieldnames, delimiter='\t')
        csv_writer.writerow({'TransactionsID': transactionID, 'Date': date_of_transaction,
                             'Creditor': sender_legal_name, 'Debtor': receiver_legal_name, 'Amount': amount, 'Balance': str(new_balance)})
        receiver.balance = str(new_balance)
        receiver.save()
        return 'Transaction Successful!'
