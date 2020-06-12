import csv
import os
from django.contrib.staticfiles.storage import staticfiles_storage

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read(accnum):
    list_of_transactions = []
    with open(staticfiles_storage.path('logs/' + accnum + '.csv'), 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter='\t')
        list_of_transactions = list(csv_reader)
    list_of_transactions.pop(0)
    return list_of_transactions
