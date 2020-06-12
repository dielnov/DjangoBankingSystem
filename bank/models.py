from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils.translation import ugettext_lazy as _
from django.utils.http import urlquote
from django.core.mail import send_mail
from bank.generator import accountNumber, regNumber, getMyDate, getMyDatePlusMonth, getMyTime, getMySec
from ckeditor.fields import RichTextField
from django_cleanup import cleanup


def user_passportPhoto_uploader(instance, filename):
    return "%s/passportPhoto/%s_passportPhoto_%s_%s_%s_%s" % (instance.account.username, instance.account.username, getMyTime().replace(':', '_'), getMySec(), getMyDate().replace('-', '_'), filename)


def kin_passportPhoto_uploader(instance, filename):
    return "%s/kinPassportPhoto/%s_kinPassportPhoto_%s_%s_%s_%s" % (instance.account.username, instance.account.username, getMyTime().replace(':', '_'), getMySec(), getMyDate().replace('-', '_'), filename)


def company_logo_uploader(instance, filename):
    return "%s/companyLogo/%s_companyLogo_%s_%s_%s_%s" % (instance.account.username, instance.account.username, getMyTime().replace(':', '_'), getMySec(), getMyDate().replace('-', '_'), filename)


def product_image_uploader(instance, filename):
    return "%s/products/%s_%s_%s_%s_%s_%s_%s" % (instance.account.username, instance.productName, instance.productbrand, instance.productModel, getMyTime().replace(':', '_'), getMySec(), getMyDate().replace('-', '_'), filename)


def loan_application_uploader(instance, filename):
    import os
    f_name, f_ext = os.path.splitext(filename)
    file_name = instance.reference+f_ext
    return "%s/Loan_Applications/%s" % (instance.account.username, file_name)
# Create your models here. #


class MyAccountManager(BaseUserManager):
    def create_user(self, email, username, isCorporate, password=None, **kwargs):
        if not email:
            raise ValueError('Users must have an email address')
        if not username:
            raise ValueError('Users must have a username')

        user = self.model(
            email=self.normalize_email(email),
            username=username,
            isCorporate=isCorporate,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **kwargs):
        user = self.create_user(
            email=self.normalize_email(email),
            username=username,
            password=password,
            isCorporate=True,
        )
        user.is_staff = True
        user.is_admin = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class Account(AbstractBaseUser):
    # Account Login Details #
    email = models.EmailField(
        verbose_name='email', max_length=60, unique=True)
    username = models.CharField(max_length=30, unique=True)
    isCorporate = models.BooleanField(default=False)
    physicalAddress = models.CharField(max_length=60)
    postalAddress = models.CharField(max_length=60)
    phone = models.CharField(max_length=30)

    date_joined = models.DateTimeField(
        verbose_name='date joined', auto_now_add=True)
    last_login = models.DateTimeField(
        verbose_name='last login', auto_now=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'isCorporate']

    objects = MyAccountManager()

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        if self.isCorporate:
            try:
                return CorporateAccount.objects.get(account=self).legalEntityName
            except:
                return self.username
        else:
            try:
                ind = IndividualAccount.objects.get(account=self)
                return ind.title + ' ' + ind.firstName + ' ' + ind.lastName
            except:
                return self.username

    # For checking permissions. to keep it simple all admin have ALL permissons
    def has_perm(self, perm, obj=None):
        return self.is_admin

    # Does this user have permission to view this app? (ALWAYS YES FOR SIMPLICITY)
    def has_module_perms(self, app_label):
        return True

    def get_absolute_url(self):
        return "/users/%s/" % urlquote(self.email)

    def get_full_name(self):
        full_name = '%s %s' % (self.legalEntityName, self.usrname)
        return full_name.strip()

    def get_short_name(self):
        return self.username

    def email_user(self, subject, message, from_email=None):
        send_mail(subject, message, from_email, [self.email])


class CorporateAccount(models.Model):
    account = models.ForeignKey(
        Account, on_delete=models.CASCADE)
    # Legal Entity Details
    legalEntityName = models.CharField(max_length=60)
    tradingAs = models.CharField(max_length=60)
    logo = models.ImageField(null=True, blank=True,
                             upload_to=company_logo_uploader)
    registrationNum = models.CharField(max_length=60, unique=True)
    entityType = models.CharField(max_length=60)
    industrySector = models.CharField(max_length=60)
    dateOfReg = models.DateField(
        verbose_name='date of registration', auto_now_add=True)
    countryOfReg = models.CharField(max_length=60)

    # Business Contact Info #
    contact1 = models.CharField(max_length=60)
    contact2 = models.CharField(max_length=60)
    website = models.CharField(max_length=60)

    pOS = models.BooleanField(default=False)

    def __str__(self):
        return self.legalEntityName + ' (' + self.industrySector + ')'


class IndividualAccount(models.Model):
    account = models.ForeignKey(
        Account, on_delete=models.CASCADE)
    #Personal Details#
    title = models.CharField(max_length=8)
    firstName = models.CharField(max_length=60)
    middleName = models.CharField(max_length=60, blank=True)
    lastName = models.CharField(max_length=60)
    isMale = models.BooleanField()
    maidenName = models.CharField(max_length=60, blank=True)
    passportPhoto = models.ImageField(upload_to=user_passportPhoto_uploader)
    nationalID = models.CharField(max_length=60)
    dob = models.CharField(max_length=60)
    maritalStatus = models.CharField(max_length=60)
    countryOfResidence = models.CharField(max_length=60)
    Nationality = models.CharField(max_length=60)
    passportNum = models.CharField(max_length=60)
    passportIssuerCountry = models.CharField(max_length=60)
    passportIssueDate = models.CharField(max_length=60)
    passportExpiryDate = models.CharField(max_length=60)

    #Contact Info#
    yearsAtResidence = models.CharField(max_length=60)
    residentialStatus = models.CharField(max_length=60)

    #Work Details#
    sourceOfIncome = models.CharField(max_length=60)
    workAddress = models.CharField(max_length=60)
    workPhone = models.CharField(max_length=60)
    workDesignation = models.CharField(max_length=60)
    grossMonthlyIncome = models.CharField(max_length=60)
    otherSourceOfIncome = models.CharField(max_length=60)

    #Next Of Kin#
    kin_fname = models.CharField(max_length=60)
    kin_sname = models.CharField(max_length=60)
    kin_phone = models.CharField(max_length=60)
    kin_address = models.CharField(max_length=60)
    kin_passportPhoto = models.ImageField(
        upload_to=kin_passportPhoto_uploader)

    def __str__(self):
        return self.title + ' ' + self.firstName + ' ' + self.lastName


class AccountDetail(models.Model):
    account = models.ForeignKey(
        Account, related_name='details', on_delete=models.CASCADE)
    # Account Details #
    accnum = models.CharField(max_length=30, unique=True)
    cardnum = models.CharField(max_length=30, unique=True)
    acctype = models.CharField(max_length=30)
    balance = models.CharField(max_length=30)
    currency = models.CharField(max_length=30)
    branch = models.CharField(max_length=30)
    cIF = models.CharField(max_length=30)
    aTM = models.BooleanField(default=False)

    def __str__(self):
        return self.accnum + ' (' + self.acctype + ')'


class test1(models.Model):
    name = models.CharField(max_length=50)
    mname = models.CharField(max_length=50)
    lname = models.CharField(max_length=50)


class test2(models.Model):
    name = models.CharField(max_length=50)
    mname = models.CharField(max_length=50)
    lname = models.CharField(max_length=50)


@cleanup.ignore
class Product(models.Model):
    account = models.ForeignKey(
        Account, related_name='product', on_delete=models.CASCADE)
    productName = models.CharField(max_length=30)
    productbrand = models.CharField(max_length=30)
    productModel = models.CharField(max_length=30)
    price = models.IntegerField()
    location = models.CharField(max_length=30)
    tag = models.CharField(max_length=30)
    description = RichTextField()
    image1 = models.ImageField(upload_to=product_image_uploader)
    image2 = models.ImageField(
        null=True, blank=True, upload_to=product_image_uploader)
    image3 = models.ImageField(
        null=True, blank=True, upload_to=product_image_uploader)
    image4 = models.ImageField(
        null=True, blank=True, upload_to=product_image_uploader)

    class Meta:
        ordering = ['-pk']

    def __str__(self):
        return str(self.pk) + ' ' + self.productName + ' ' + self.productbrand + ' ' + self.productModel


class Claim(models.Model):
    account = models.ForeignKey(
        Account, related_name='claim', on_delete=models.CASCADE)
    productName = models.CharField(max_length=30)
    productbrand = models.CharField(max_length=30)
    productModel = models.CharField(max_length=30)
    price = models.CharField(max_length=30)
    location = models.CharField(max_length=30)
    tag = models.CharField(max_length=30)
    description = models.CharField(max_length=30)
    image1 = models.ImageField(upload_to=product_image_uploader)
    image2 = models.ImageField(
        null=True, blank=True, upload_to=product_image_uploader)
    image3 = models.ImageField(
        null=True, blank=True, upload_to=product_image_uploader)
    image4 = models.ImageField(
        null=True, blank=True, upload_to=product_image_uploader)
    claimer = models.CharField(max_length=30)
    reference = models.CharField(max_length=30, blank=True)
    viewed = models.BooleanField(default=False)
    dealStatus = models.CharField(max_length=30,
                                  choices=(('P', 'Pending'), ('S', 'Successful'), ('F', 'Failed')))
    dealComment = RichTextField()
    claim_date = models.DateTimeField(verbose_name='date of claim')
    claim_exp_date = models.DateTimeField(verbose_name='claim expiry date')

    class Meta:
        ordering = ['-claim_date']


class LoanApplication(models.Model):
    account = models.ForeignKey(Account, related_name='application', on_delete=models.CASCADE)
    payslip = models.FileField(null=True, blank=True, upload_to=loan_application_uploader)
    proofOfEmployment = models.FileField(null=True, blank=True, upload_to=loan_application_uploader)
    proofOfResidence = models.FileField(null=True, blank=True, upload_to=loan_application_uploader)
    copyOfID = models.FileField(null=True, blank=True, upload_to=loan_application_uploader)
    reference = models.CharField(max_length=30, default=regNumber())
    viewed = models.BooleanField(default=False)
    pending = models.BooleanField(default=True)
    approval = models.BooleanField(default=False)
    applicationDate = models.DateTimeField(verbose_name='dateApplied', auto_now_add=True)

    class Meta:
        ordering = ['-applicationDate']
