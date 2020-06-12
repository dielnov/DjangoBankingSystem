"""chenai URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from .views import (
    index,
    login_view,
    account_view,
    logout_view,
    registration_view,
    corporate_create_view,
    individual_create_view,
    AccountDetails,
    fundsTransfer,
    statement,
    application,
    agreement,
    catalog,
    claims,
    fails,
    notifications,
    post,
    product,
    claimedProduct,
    profile,
    succesful,
    dashboard,
    loans,
    viewApplication,
    approve,
    decline,
    user_list,
    user_update,
    cat_search,
)

app_name = 'bank'

urlpatterns = [
    path('', index, name='index'),
    path('login', login_view, name='login'),
    path('account', account_view, name='account'),
    path('logout', logout_view, name='logout'),
    path('register', registration_view, name='register'),
    path('corporate_application', corporate_create_view, name='corporate'),
    path('individual_application', individual_create_view, name='individual'),
    path('account_details', AccountDetails, name='details'),
    path('funds_transfer', fundsTransfer, name='fundsTransfer'),
    path('statement', statement, name='statement'),
    path('agreement/<int:pk>', agreement, name='agreement'),
    path('application', application, name='application'),
    path('catalog', catalog, name='catalog'),
    path('claims', claims, name='claims'),
    path('fails', fails, name='fails'),
    path('notifications', notifications, name='notifications'),
    path('post', post, name='post'),
    path('product/<int:pk>', product, name='product'),
    path('claimed_product/<int:pk>', claimedProduct, name='claimed_product'),
    path('profile', profile, name='profile'),
    path('succesful', succesful, name='succesful'),
    path('dashboard', dashboard, name='dashboard'),
    path('loans', loans, name='loans'),
    path('view_application/<int:pk>', viewApplication, name='view_application'),
    path('approve/<int:pk>', approve, name='approve'),
    path('decline/<int:pk>', decline, name='decline'),
    path('user_list', user_list, name='user_list'),
    path('user_update/<int:pk>', user_update, name='user_update'),
    path('cat_search', cat_search, name='cat_search'),
]
