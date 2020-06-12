import csv
import os
from django.contrib.staticfiles.storage import staticfiles_storage

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def makeCSV(accnum, s_name):
    with open(staticfiles_storage.path('logs/' + accnum + '.csv'), 'w', newline='') as new_file:
        fieldnames = ['TransactionsID', 'Date',
                      'Creditor', 'Debtor', 'Amount', 'Balance']
        csv_writer = csv.DictWriter(
            new_file, fieldnames=fieldnames, delimiter='\t')
        csv_writer.writeheader()
        csv_writer.writerow({'TransactionsID': 'TRIDXXXXXXXX-XX:XX', 'Date': 'XX-XX-XXXX',
                             'Creditor': 'XXXXXXXXXX', 'Debtor': 'XXXXXXXXXX', 'Amount': '$XXX.XX', 'Balance': '0'})

    return accnum + '.csv created succesfully! from ' + s_name

