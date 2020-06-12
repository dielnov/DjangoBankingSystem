from django.contrib import admin
from .models import Account, IndividualAccount, CorporateAccount, AccountDetail, Product, Claim, LoanApplication

# Register your models here.
admin.site.register(Account)
admin.site.register(IndividualAccount)
admin.site.register(CorporateAccount)
admin.site.register(AccountDetail)
admin.site.register(Product)
admin.site.register(Claim)
admin.site.register(LoanApplication)
