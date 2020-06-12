from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, FileResponse
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib import messages
from .forms import RegistrationForm, AccountAuthenticationForm, AccountUpdateForm, CorporateCreateForm, IndividualCreateForm, AccountDetailForm, ProductForm
from .models import Account, CorporateAccount, IndividualAccount, AccountDetail, Product, test1, test2, Claim, LoanApplication
from bank.generator import accountNumber, regNumber, getMyDate, getMyDatePlusMonth
from bank.create_csv import makeCSV
from bank.transaction import transact
from bank.read_csv import read
from bank.model_ops import cpy, mve
from django.db.models import Q
import os


def index(request):
    if not request.user.is_authenticated:
        return render(request, 'bank/index.html')
    else:
        if request.user.is_superuser:
            return redirect('bank:dashboard')
        else:
            return account_view(request)


@login_required
def logout_view(request):
    logout(request)
    return redirect('bank:index')


def login_view(request):
    context = {}
    user = request.user
    if user.is_authenticated:
        return redirect("bank:account")
    if request.POST:
        form = AccountAuthenticationForm(request.POST)
        if form.is_valid():
            email = request.POST['email']
            password = request.POST['password']
            user = authenticate(email=email, password=password)
            if user:
                login(request, user)
                if not request.user.is_superuser:
                    return redirect("bank:account")
                else:
                    return redirect("bank:dashboard")
    else:
        form = AccountAuthenticationForm()
        context['login_form'] = form
    return render(request, "bank/login.html", context)


def registration_view(request):
    context = {}
    if request.POST:
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save(commit=False)
            email = form.cleaned_data.get('email')
            username = form.cleaned_data.get('username')
            isCorporate = form.cleaned_data.get('isCorporate')
            raw_password = form.cleaned_data.get('password1')
            get_user_model().objects.create_user(
                email=email, username=username, isCorporate=isCorporate, password=raw_password)
            return redirect('bank:login')
        else:
            context['registration_form'] = form
    else:
        form = RegistrationForm()
        context['registration_form'] = form
    return render(request, 'bank/register.html', context)

@login_required
def account_view(request):
    context = {}

    try:
        details = AccountDetail.objects.get(account=request.user)
        context['details'] = details
    except:
        print(
            "Missing Account Details! User Must Complete Application Under 'Credentials'.")
        context['no_details'] = True

    if request.user.isCorporate:
        try:
            corporate = CorporateAccount.objects.get(account=request.user)
            context['corporate'] = corporate
        except:
            print("Corporate Account Not Available!")
    else:
        try:
            individual = IndividualAccount.objects.get(account=request.user)
            context['individual'] = individual
        except:
            print("Individual Account Not Available!!")

    if not request.user.is_authenticated:
        return redirect("bank:login")
    else:
        return render(request, "bank/account.html", context)

@login_required
def corporate_create_view(request):
    context = {}
    if request.method == 'POST':
        try:
            # UpdateProfile If It Exists Already
            corporate = CorporateAccount.objects.get(account=request.user)
            form = CorporateCreateForm(
                request.POST, request.FILES, instance=corporate)
            context['corporate'] = corporate
            if form.is_valid():
                form.save()
            context['form'] = form
            print("Update View Seg")
            return redirect('bank:account')
        except:
            # If It Doesnt Exist Then Create One
            form = CorporateCreateForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                context['form'] = form
                print("Create View Seg")
            else:
                print(form.errors)
            return redirect('bank:details')
    else:
        try:
            # Get Profile Into Form If It Exists
            corporate = CorporateAccount.objects.get(account=request.user)
            form = CorporateCreateForm(instance=corporate)
            context['form'] = form
            context['corporate'] = corporate
        except:
            # Otherwise Get Blank Form
            form = CorporateCreateForm()
            context['form'] = form
            context['reg'] = regNumber()
        return render(request, 'bank/corporate_create_form.html', context)

@login_required
def individual_create_view(request):
    context = {}
    if request.method == 'POST':
        try:
            # UpdateProfile If It Exists Already
            individual = IndividualAccount.objects.get(account=request.user)
            form = IndividualCreateForm(
                request.POST, request.FILES, instance=individual)
            context['individual'] = individual
            if form.is_valid():
                form.save()
                context['form'] = form
            print('update....')
            try:
                details = AccountDetail.objects.get(account=request.user)
                print('update....available details')
                return redirect('bank:individual')
            except:
                print('update....no details')
                return redirect('bank:details')

        except:
            # If It Doesnt Exist Then Create One
            form = IndividualCreateForm(request.POST, request.FILES)
            form.cleaned_data

            if form.is_valid():
                form.save()
                context['form'] = form
            else:
                print(form.errors)
            return redirect('bank:details')
    else:
        try:
            # Get Profile Into Form If It Exists
            individual = IndividualAccount.objects.get(account=request.user)
            form = IndividualCreateForm(instance=individual)
            context['individual'] = individual
        except:
            # Otherwise Get Blank Form
            form = IndividualCreateForm()
    context['form'] = form
    return render(request, 'bank/individual_create_form.html', context)

@login_required
def AccountDetails(request):
    context = {}
    if request.method == 'POST':
        try:
            # UpdateProfile If It Exists Already
            details = AccountDetail.objects.get(account=request.user)
            form = AccountDetailForm(
                request.POST, request.FILES, instance=details)
            context['details'] = details
            if form.is_valid():
                form.save()
                context['form'] = form
            return redirect('bank:details')
        except:
            # If It Doesnt Exist Then Create One
            form = AccountDetailForm(request.POST, request.FILES)
            if form.is_valid():
                accountNum = form.cleaned_data.get('accnum')
                form.save(commit=False)
                print(makeCSV(accountNum, 'Create New Account Details.'))
                detail = AccountDetail()
                detail.account = request.user
                detail.accnum = accountNum
                detail.cardnum = form.cleaned_data.get('cardnum')
                detail.acctype = form.cleaned_data.get('acctype')

                income = IndividualAccount.objects.get(account=request.user).grossMonthlyIncome
                est_loan = int(income) * 18
                detail.balance = str(est_loan)
                detail.currency = form.cleaned_data.get('currency')
                detail.branch = form.cleaned_data.get('branch')
                detail.cIF = form.cleaned_data.get('cIF')
                detail.aTM = form.cleaned_data.get('aTM')
                detail.save()
                context['form'] = form
                return redirect('bank:account')
            else:
                print(form.errors)
                return redirect('bank:details')
    else:
        try:
            # Get Profile Into Form If It Exists
            details = AccountDetail.objects.get(account=request.user)
            form = AccountDetailForm(instance=details)
            print('get details...')
            context['details'] = details
        except:
            # Otherwise Get Blank Form
            form = AccountDetailForm()
            context['form'] = form
            context['acc'] = accountNumber()
            context['cif'] = context['acc'][0:4] + context['acc'][5:8]
            income = IndividualAccount.objects.get(
                account=request.user).grossMonthlyIncome
            est_loan = int(income) * 18
            context['est_loan'] = est_loan
        return render(request, 'bank/account_details_form.html', context)

@login_required
def fundsTransfer(request):
    context = {}
    try:
        sender = AccountDetail.objects.get(account=request.user)
        if request.method == 'POST':
            tradingAs = request.POST['tradingAs']
            phone = request.POST['phone']
            bank = request.POST['receivingBank']
            accnum = request.POST['accnum']
            branch = request.POST['branch']
            date = request.POST['date']
            currency = request.POST['currency']
            amount = request.POST['amount']
            myMessage = transact(sender.accnum, accnum, amount)
            context['message'] = myMessage
            print('out fundsTransfer running...')
        return render(request, 'bank/funds_transfer.html', context)
    except:
        context['messages'] = "Account Not Yet Activated!"
        return render(request, "bank/account.html", context)


@login_required
def statement(request):
    context = {}
    try:
        details = AccountDetail.objects.get(account=request.user)
    except:
        context['messages'] = "Account Not Yet Activated!"
        return render(request, "bank/account.html", context)

    list_of_transactions = read(str(details.accnum))
    context['transactions'] = list_of_transactions
    return render(request, 'bank/statement.html', context)

######################################################################################################
######################################################################################################
######################################################################################################
######################################################################################################
######################################################################################################
#######################################Loans Views####################################################
######################################################################################################
######################################################################################################
######################################################################################################
######################################################################################################
######################################################################################################

@login_required
def application(request):
    if not AccountDetail.objects.get(account=request.user):
        return redirect('bank:account')

    context = {}
    if request.method == 'POST':
        account = request.user
        payslip = request.FILES.get('payslip')
        proofOfEmployment = request.FILES.get('proofOfEmployment')
        proofOfResidence =request.FILES.get('proofOfResidence')
        copyOfID = request.FILES.get('copyOfID')
        loanApplication = LoanApplication.objects.create(account=account, payslip=payslip, proofOfEmployment=proofOfEmployment, proofOfResidence=proofOfResidence,copyOfID=copyOfID,reference=regNumber())
        loanApplication.save()
        return redirect('bank:application')
    else:
        try:
            loans = LoanApplication.objects.filter(account=request.user)
            context['loans'] = loans
        except:
            context['message'] = 'Not yet applied for any loan'
        return render(request, 'loans/application.html', context)


@login_required
def agreement(request, pk):
    context = {}
    product = Product.objects.get(pk=pk)
    notifications = Claim.objects.filter(account=request.user, viewed=False)
    context = {
        'product': product,
        'today': getMyDate(),
        'expiryDate': getMyDatePlusMonth(),
        'notifications': notifications,
    }
    if request.method == 'POST':
        # Check Form Data
        # If Valid Save Agreement
        # Put Product Into Claim&Notifications
        product = Product.objects.get(pk=pk)
        claim = Claim()
        mve(request, product, claim)
        return redirect('bank:catalog')
    return render(request, 'loans/agreement.html', context)


@login_required
def catalog(request):
    context = {}
    est_loan = int(AccountDetail.objects.get(account=request.user).balance)
    products = Product.objects.filter(price__lte=est_loan)
    if len(products) == 0:
        context['empty'] = str(est_loan)
    context['products'] = products
    notifications = Claim.objects.filter(account=request.user, viewed=False)
    context['notifications'] = notifications
    return render(request, 'loans/catalog.html', context)

@login_required
def cat_search(request):
    template = 'loans/catalog.html'
    context = {}
    query = request.GET.get('q')
    products = Product.objects.filter(Q(productName__icontains=query) | Q(productbrand__icontains=query) | Q(productModel__icontains=query) | Q(description__icontains=query) | Q(price__icontains=query) )
    context['products'] = products
    return render(request,template,context)



@login_required
def claims(request):
    claimList = Claim.objects.filter(claimer=request.user)
    notifications = Claim.objects.filter(account=request.user, viewed=False)
    context = {
        'claimList': claimList,
        'notifications': notifications,
    }
    return render(request, 'loans/claims.html', context)


@login_required
def fails(request):
    notifications = Claim.objects.filter(account=request.user, viewed=False)
    context['notifications'] = notifications
    return render(request, 'loans/fails.html', context)


@login_required
def notifications(request):
    viewed_notifications = Claim.objects.filter(
        account=request.user, viewed=True)
    new_notifications = Claim.objects.filter(
        account=request.user, viewed=False)
    for new_notification in new_notifications:
        new_notification.viewed = True
        new_notification.save()
    context = {
        'viewed_notifications': viewed_notifications,
        'new_notifications': new_notifications,
    }
    return render(request, 'loans/notifications.html', context)


@login_required
def post(request):
    context = {}
    notifications = Claim.objects.filter(account=request.user, viewed=False)
    context['notifications'] = notifications
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
        else:
            print(form.errors)
        return redirect('bank:catalog')
    else:
        form = ProductForm()
        context['form'] = form
        return render(request, 'loans/post_form.html', context)


@login_required
def product(request, pk):
    context = {}
    notifications = Claim.objects.filter(account=request.user, viewed=False)
    context['notifications'] = notifications
    try:
        product = Product.objects.get(pk=pk)
        context['product'] = product
        photos = []
        pictures = [product.image1, product.image2,
                    product.image3, product.image4]
        for pic in pictures:
            if pic:
                photos.append(pic)
            else:
                break
        context['photos'] = photos
    except:
        return redirect('bank:catalog')
    return render(request, 'loans/product.html', context)


@login_required
def claimedProduct(request, pk):
    context = {}
    notifications = Claim.objects.filter(account=request.user, viewed=False)
    context['notifications'] = notifications
    product = Claim.objects.get(pk=pk)
    context['product'] = product
    photos = []
    pictures = [product.image1, product.image2,
                product.image3, product.image4]
    for pic in pictures:
        if pic:
            photos.append(pic)
        else:
            break
    context['photos'] = photos
    return render(request, 'loans/claimedProduct.html', context)


@login_required
def profile(request):
    notifications = Claim.objects.filter(account=request.user, viewed=False)
    context['notifications'] = notifications
    return render(request, 'loans/profile.html')


@login_required
def succesful(request):
    notifications = Claim.objects.filter(account=request.user, viewed=False)
    context['notifications'] = notifications
    return render(request, 'loans/succesful.html')

######################################################################################################
######################################################################################################
######################################################################################################
######################################################################################################
######################################################################################################
#######################################SysAdmin Views####################################################
######################################################################################################
######################################################################################################
######################################################################################################
######################################################################################################
######################################################################################################
@login_required
def dashboard(request):
    if not request.user.is_superuser:
        return redirect('bank:account')
    new_loans = LoanApplication.objects.filter(viewed=False)
    context = {
        'new_loans': new_loans,
    }
    return render(request, 'sys_admin/index.html',context)


@login_required
def loans(request):
    if not request.user.is_superuser:
        return redirect('bank:account')
    new_loans = LoanApplication.objects.filter(viewed=False)
    viewed_loans = LoanApplication.objects.filter(viewed=True)
    context = {
        'new_loans':new_loans,
        'viewed_loans':viewed_loans,
    }
    for new_loan in new_loans:
        new_loan.viewed = True
        new_loan.save()
    return render(request, 'sys_admin/loans.html',context)


@login_required
def viewApplication(request,pk):
    if not request.user.is_superuser:
        return redirect('bank:account')
    new_loans = LoanApplication.objects.filter(viewed=False)
    context = {
        'new_loans': new_loans,
    }
    loan = LoanApplication.objects.get(reference=pk)
    info = IndividualAccount.objects.get(account=loan.account)
    detail = AccountDetail.objects.get(account=loan.account)

    context = {
                'loan':loan,
                'info':info,
                'detail':detail,
                }
    return render(request,'sys_admin/application.html',context)


@login_required
def approve(request,pk):
    if not request.user.is_superuser:
        return redirect('bank:account')
    new_loans = LoanApplication.objects.filter(viewed=False)
    context = {
        'new_loans': new_loans,
    }
    loan = LoanApplication.objects.get(pk=pk)
    loan.approval = True
    loan.pending = False
    loan.save()
    return redirect('bank:loans')


@login_required
def decline(request, pk):
    if not request.user.is_superuser:
        return redirect('bank:account')
    new_loans = LoanApplication.objects.filter(viewed=False)
    context = {
        'new_loans': new_loans,
    }
    loan = LoanApplication.objects.get(pk=pk)
    loan.approval = False
    loan.pending = False
    loan.save()
    return redirect('bank:loans')

@login_required
def user_list(request):
    if not request.user.is_superuser:
        return redirect('bank:account')
    listOfUsers = Account.objects.all()
    context = {
        'listOfUsers': listOfUsers,
    }
    return render(request,'sys_admin/users.html',context)

@login_required
def user_update(request,pk):
    if not request.user.is_superuser:
        return redirect('bank:account')
    context = {}
    account = Account.objects.get(pk=pk)
    if request.method == 'POST':
        try:
            # UpdateProfile If It Exists Already
            form = AccountUpdateForm(request.POST, instance=account)
            context['account'] = account
            if form.is_valid():
                form.save()
            context['form'] = form
            return redirect('bank:user_update', pk=pk)
        except Exception as e:
           print(e)
           return redirect('bank:user_update', pk=pk)

    else:
        form = AccountUpdateForm(instance=account)
        context['form'] = form
        return render(request, 'sys_admin/user_update_form.html', context)
    
