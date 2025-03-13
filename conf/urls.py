"""
URL configuration for conf project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib.auth.views import LogoutView

from django.contrib import admin
from django.urls import path, include

from rest_framework import routers
from rest_framework.authtoken.views import obtain_auth_token

from core.views import Logout, MemberViewSet, GroupViewSet, ProfileViewSet, ChangePasswordView
from purchase.models import ProvisionRequest

REGISTER = 'register'
SIGN_IN = 'sign_in'
DO_SIGN_IN = 'do_sign_in'
LOGOUT = 'logout'
ACCOUNT_SETUP = 'account_setup'
UPDATE_INFO = 'update_info'
UPDATE_PASSWORD = 'update_password'
SERVICE_DETAIL = 'service_detail'
SERVICE_EXPIRED = 'service_expired'
LOAD_EVENT = 'load_event_content'
PHONE_CONFIRMATION = 'phone_confirmation'
EMAIL_CONFIRMATION = 'email_confirmation'
CONFIRM_EMAIL = 'confirm_email'
STAFF_ROUTER = 'staff_router'
UPDATE_WEBLET = 'update_weblet_status'

logout_redirect_url = getattr(settings, "LOGOUT_REDIRECT_URL", None)
if not logout_redirect_url:
    logout_redirect_url = getattr(settings, 'LOGIN_URL')

router = routers.DefaultRouter()

router.register(r'provision-requests', ProvisionRequestViewSet)
router.register(r'purchases', PurchaseViewSet)
router.register(r'providers', ProviderViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'products', ProductViewSet)

urlpatterns = [
    path('laakam/', admin.site.urls),
    path('logout', LogoutView.as_view(), {'next_page': logout_redirect_url}, name=LOGOUT),
    path('signOut', LogoutView.as_view(), {'next_page': logout_redirect_url}),
    path('signIn', SignIn.as_view(), name='sign_in'),
    path('signIn', SignInMinimal.as_view(), name=SIGN_IN),
    path('doSignIn', SignIn.as_view(), name=DO_SIGN_IN),
    path('register', Register.as_view(), name=REGISTER),

    path('accountSetup/', login_required(AccountSetup.as_view()), name='account_setup'),
    path('update_info', update_info, name=UPDATE_INFO),
    path('update_password', update_password, name=UPDATE_PASSWORD),

    path('forgottenPassword/', ForgottenPassword.as_view(), name='forgotten_password'),
    path('setNewPassword/<slug:uidb64>/<slug:token>/', SetNewPassword.as_view(), name='set_new_password'),
    path('setNewPasswordSMSRecovery/', SetNewPasswordSMSRecovery.as_view(), name='set_new_password_sms_recovery'),
    path('profile/<member_id>/', login_required(Profile.as_view()), name='profile'),
    path('dashboard/', DashboardBase.as_view(), name='dashboard'),

    path('upload_image', upload, name='upload_image'),
    path('upload', upload, name='upload'),  # An alias for upload_image that looks less confusing

    # API upload
    path('upload_file/', upload_file, name='upload_file'),
    path('', include('purchase.urls'), name='purchase'),
]
