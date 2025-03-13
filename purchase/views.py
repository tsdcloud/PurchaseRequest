# Create your views here.
import json
import os
import random
import string
import uuid
from datetime import datetime, timedelta
from threading import Thread

from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
# from django.contrib.auth.handlers.modwsgi import check_password
from django.contrib.auth.hashers import check_password
from django.core.checks import messages
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import transaction
from django.db.models import Q, F, Sum
from django.dispatch import receiver
from django.utils.decorators import method_decorator
from django.utils.http import urlunquote
from django.views.decorators.cache import never_cache, cache_page
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import TemplateView
from rest_framework.generics import UpdateAPIView
from slugify import slugify
from xhtml2pdf import pisa
from num2words import num2words
from decimal import Decimal

from django.conf import settings
from django.contrib.staticfiles import finders
from django.contrib.auth.models import Permission
from django.contrib.auth.models import Group
from django.shortcuts import render, get_object_or_404
from django.contrib.humanize.templatetags.humanize import intcomma
from django.template.loader import get_template
from django.utils.translation import gettext_lazy as _
from django.core.mail import EmailMessage
from django.http import HttpResponseBadRequest, HttpResponse, Http404, QueryDict, HttpResponseRedirect
from django.urls import reverse, NoReverseMatch
from django_rest_passwordreset.signals import reset_password_token_created

from rest_framework.authtoken.models import Token
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.decorators import api_view, permission_classes, authentication_classes, action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.request import Request
from rest_framework import permissions
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView

from commons.forms import test_fake_email, MemberForm, SMSPasswordResetForm, PasswordResetForm, SetPasswordForm, \
    SetPasswordFormSMSRecovery, MemberUpdateForm
from commons.models import Member
from core.utils import send_sms


class Register(TemplateView):
    template_name = 'accesscontrol/register.html'

    def get_context_data(self, **kwargs):
        context = super(Register, self).get_context_data(**kwargs)
        return context

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            next_url = request.GET.get('next')
            if next_url:
                return HttpResponseRedirect(next_url)
            else:
                next_url_view = getattr(settings, 'LOGIN_REDIRECT_URL', None)
                if next_url_view:
                    next_url = reverse(next_url_view)
                else:
                    next_url = ikwenize(reverse('ikwen:console'))
            return HttpResponseRedirect(next_url)
        return super(Register, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        form = MemberForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username'].strip().lower()
            phone = form.cleaned_data.get('phone', '')
            email = form.cleaned_data.get('email', '').strip().lower()
            first_name = form.cleaned_data.get('first_name', '').strip()
            last_name = form.cleaned_data.get('last_name', '').strip()
            gender = form.cleaned_data.get('gender')
            try:
                year = request.POST['year']
                month = request.POST['month']
                day = request.POST['day']
                dob = datetime(int(year), int(month), int(day))
            except:
                dob = None
            sign_in_url = reverse('ikwen:register')
            query_string = request.META.get('QUERY_STRING')
            try:
                validate_email(username)
                test_fake_email(username)
                email = username
            except ValidationError:
                pass
            if not email:
                email = '__%s__@ikwen.com' % username
            try:
                member = Member.objects.get(username=username)
                if member.is_ghost:
                    raise Member.DoesNotExist()
            except Member.DoesNotExist:
                if phone or email:
                    try:
                        member = Member.objects.get(Q(phone=phone) | Q(email=email))
                        if member.is_ghost:
                            raise Member.DoesNotExist()
                    except Member.DoesNotExist:
                        pass
                    else:
                        msg = _("You already have an account with this email or phone. Use it to login.")
                        messages.info(request, msg)
                        if query_string:
                            sign_in_url += "?" + query_string
                        return HttpResponseRedirect(sign_in_url)
                password = form.cleaned_data['password']
                password2 = form.cleaned_data['password2']
                if password != password2:
                    msg = _("Sorry, passwords mismatch.")
                    messages.error(request, msg)
                    register_url = reverse('ikwen:register')
                    if query_string:
                        register_url += "?" + query_string
                    return HttpResponseRedirect(register_url)
                Member.objects.create_user(username=username, phone=phone, email=email, password=password,
                                           first_name=first_name, last_name=last_name, dob=dob, gender=gender)
                member = authenticate(username=username, password=password)
                login(request, member)
                events = getattr(settings, 'IKWEN_REGISTER_EVENTS', ())
                for path in events:
                    event = import_by_path(path)
                    event(request, *args, **kwargs)
                reward_pack_list = None
                if not getattr(settings, 'IS_IKWEN', False):
                    service = get_service_instance()
                    set_counters(service)
                    increment_history_field(service, 'community_history')
                pwa_profile_id = request.COOKIES.get('pwa_profile_id')
                if pwa_profile_id:
                    PWAProfile.objects.filter(pk=pwa_profile_id).update(member=member)
                send_welcome_email(member, reward_pack_list)
                if request.GET.get('join'):
                    return join(request, *args, **kwargs)
                next_url = request.GET.get('next')
                if next_url:
                    # Remove next_url from the original query_string
                    next_url = next_url.split('?')[0]
                    query_string = urlunquote(query_string).replace('next=%s' % next_url, '').strip('?').strip('&')
                    next_url += "?" + query_string
                else:
                    next_url_view = getattr(settings, 'REGISTER_REDIRECT_URL', None)
                    if not next_url_view:
                        next_url_view = getattr(settings, 'LOGIN_REDIRECT_URL', None)
                    if next_url_view:
                        next_url = reverse(next_url_view)
                    else:
                        next_url = ikwenize(reverse('ikwen:console'))
                return HttpResponseRedirect(next_url)
            else:
                msg = _("You already have an account with this username. Use it to login.")
                messages.info(request, msg)
                if query_string:
                    sign_in_url += "?" + query_string
                return HttpResponseRedirect(sign_in_url)
        else:
            context = self.get_context_data(**kwargs)
            context['register_form'] = form
            return render(request, 'accesscontrol/register.html', context)


class SignIn(TemplateView):
    template_name = 'accesscontrol/sign_in.html'

    def get_context_data(self, **kwargs):
        context = super(SignIn, self).get_context_data(**kwargs)
        return context

    def get(self, request, *args, **kwargs):
        if kwargs.get('template_name'):
            self.template_name = kwargs.get('template_name')

        if request.user.is_authenticated:
            next_url = request.GET.get('next')
            if next_url:
                return HttpResponseRedirect(next_url)
            elif not getattr(settings, 'IS_IKWEN', False) and request.user.is_staff:
                return staff_router(request, *args, **kwargs)
            else:
                next_url_view = getattr(settings, 'LOGIN_REDIRECT_URL', None)
                if next_url_view:
                    next_url = reverse(next_url_view)
            return HttpResponseRedirect(next_url)
        return super(SignIn, self).get(request, *args, **kwargs)

    @method_decorator(sensitive_post_parameters())
    @method_decorator(never_cache)
    def post(self, request, *args, **kwargs):
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            member = form.get_user()
            login(request, member)
            events = getattr(settings, 'IKWEN_LOGIN_EVENTS', ())
            for path in events:
                event = import_by_path(path)
                event(request, *args, **kwargs)
            pwa_profile_id = request.COOKIES.get('pwa_profile_id')
            if pwa_profile_id:
                PWAProfile.objects.filter(pk=pwa_profile_id).update(member=member)
            if request.GET.get('join'):
                return join(request, *args, **kwargs)
            query_string = request.META.get('QUERY_STRING')
            next_url = request.GET.get('next')
            if next_url:
                # Remove next_url from the original query_string
                next_url = next_url.split('?')[0]
                query_string = urlunquote(query_string).replace('next=%s' % next_url, '').strip('?').strip('&')
            else:
                if not getattr(settings, 'IS_IKWEN', False) and member.is_staff:
                    return staff_router(request, *args, **kwargs)
                else:
                    next_url_view = getattr(settings, 'LOGIN_REDIRECT_URL', None)
                    if next_url_view:
                        next_url = reverse(next_url_view)
                    else:
                        next_url = ikwenize(reverse('ikwen:console'))
            if query_string:
                next_url += '?' + query_string
            return HttpResponseRedirect(next_url)
        else:
            context = self.get_context_data(**kwargs)
            context['login_form'] = form
            if form.errors:
                error_message = getattr(settings, 'IKWEN_LOGIN_FAILED_ERROR_MSG',
                                        _("Invalid username/password or account inactive"))
                context['error_message'] = error_message
            return render(request, 'accesscontrol/sign_in.html', context)


class SignInMinimal(SignIn):
    template_name = 'accesscontrol/sign_in_minimal.html'

    def get_context_data(self, **kwargs):
        context = super(SignInMinimal, self).get_context_data(**kwargs)
        return context

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            super(SignInMinimal, self).get(request, *args, **kwargs)
        username = request.GET.get('username')
        response = {'existing': False}
        if username:
            try:
                member = Member.objects.get(username__iexact=username)
                if not member.is_ghost:
                    response = {'existing': True, 'is_staff': member.is_staff}
            except Member.DoesNotExist:
                try:
                    member = Member.objects.get(email__iexact=username)
                    if not member.is_ghost:
                        response = {'existing': True, 'is_staff': member.is_staff}
                except Member.DoesNotExist:
                    try:
                        member = Member.objects.get(phone=username)
                        if not member.is_ghost:
                            response = {'existing': True, 'is_staff': member.is_staff}
                    except Member.DoesNotExist:
                        pass
            if getattr(settings, 'AUTH_WITHOUT_PASSWORD', False):
                response['no_password'] = True
            return HttpResponse(json.dumps(response), 'content-type: text/json')
        return super(SignInMinimal, self).get(request, *args, **kwargs)


@login_required
def staff_router(request, *args, **kwargs):
    """
    This view routes Staff user to his correct homepage
    as defined in the STAFF_ROUTER setting. Failing to
    """
    member = request.user
    next_url = reverse(getattr(settings, 'LOGIN_REDIRECT_URL', 'home'))
    routes = getattr(settings, 'STAFF_ROUTER', None)
    if routes:
        next_url = reverse('ikwen:staff_without_permission')
        for route in routes:
            condition = route[0]
            passed_test = False
            try:
                do_test = import_by_path(condition)
                passed_test = do_test(member)
            except:
                if member.has_perm(condition):
                    passed_test = True
            url_name = route[1]
            params = route[2] if len(route) > 2 else None
            if passed_test:
                if params:
                    if type(params) is tuple:
                        next_url = reverse(url_name, args=params)
                    else:  # params are supposed to be a dictionary here
                        next_url = reverse(url_name, kwargs=params)
                else:
                    next_url = reverse(url_name)
                break
    elif member.is_superuser:
        try:
            next_url = reverse('sudo_home')
        except NoReverseMatch:
            pass

    return HttpResponseRedirect(next_url)


class StaffWithoutPermission(TemplateView):
    template_name = 'accesscontrol/staff_without_permission.html'


class ForgottenPassword(TemplateView):
    template_name = 'accesscontrol/forgotten_password.html'

    def get_context_data(self, **kwargs):
        context = super(ForgottenPassword, self).get_context_data(**kwargs)
        sms_recovery = getattr(settings, 'PASSWORD_RECOVERY_METHOD', 'mail').lower() == 'sms'
        context['sms_recovery'] = sms_recovery
        return context

    def post(self, request, *args, **kwargs):
        # TODO: Handle mail sending failure
        sms_recovery = getattr(settings, 'PASSWORD_RECOVERY_METHOD', 'mail').lower() == 'sms'
        if sms_recovery:
            form = SMSPasswordResetForm(request.POST)
            if form.is_valid():
                request.session['phone'] = form.cleaned_data['phone']
                return HttpResponseRedirect(reverse('ikwen:set_new_password_sms_recovery'))
            else:
                context = self.get_context_data(**kwargs)
                context['form'] = form
                return render(request, self.template_name, context)
        else:
            form = PasswordResetForm(request.POST)
            if form.is_valid():
                opts = {
                    'use_https': request.is_secure(),
                    'request': request,
                }
                form.save(**opts)
                return HttpResponseRedirect(reverse('ikwen:forgotten_password'))
            else:
                context = self.get_context_data(**kwargs)
                context['form'] = form
                return render(request, self.template_name, context)


class SetNewPassword(TemplateView):
    """
    View that checks the hash in a password reset link and presents a
    form for entering a new password.
    """
    template_name = 'accesscontrol/set_new_password.html'

    def get_member(self, uidb64):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            member = Member.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, Member.DoesNotExist):
            member = None
        return member

    def get(self, request, *args, **kwargs):
        uidb64, token = kwargs['uidb64'], kwargs['token']
        member = self.get_member(uidb64)
        validlink = False
        if member is not None and default_token_generator.check_token(member, token):
            validlink = True
        context = {
            'uidb64': uidb64,
            'token': token,
            'validlink': validlink,
            'service': get_service_instance()
        }
        return render(request, self.template_name, context)

    # Doesn't need csrf_protect since no-one can guess the URL
    @method_decorator(sensitive_post_parameters())
    @method_decorator(never_cache)
    def post(self, request, uidb64, *args, **kwargs):
        member = self.get_member(uidb64)
        form = SetPasswordForm(member, request.POST)
        if form.is_valid():
            form.save()
            msg = _("Password successfully reset.")
            messages.success(request, msg)
            return HttpResponseRedirect(reverse('ikwen:sign_in'))
        else:
            context = self.get_context_data(**kwargs)
            context['form'] = form
            context['uidb64'] = uidb64
            context['token'] = kwargs['token']
            return render(request, self.template_name, context)


class SetNewPasswordSMSRecovery(TemplateView):
    template_name = 'accesscontrol/set_new_password_sms_recovery.html'

    def send_code(self, request, new_code=False, is_api=False):
        if is_api:
            phone = slugify(request.GET['phone']).replace('-', '')
        else:
            phone = slugify(request.session['phone']).replace('-', '')
        request.session['phone'] = phone
        Member.objects.get(Q(phone__endswith=phone) | Q(username__endswith=phone))  # Let exception be handled by the caller block
        service = get_service_instance()
        reset_code = ''.join([random.SystemRandom().choice(string.digits) for _ in range(4)])
        do_send = False
        try:
            current = request.session['reset_code']  # Test whether there's a pending reset_code in session
            if new_code:
                request.session['reset_code'] = reset_code
                do_send = True
        except KeyError:
            request.session['reset_code'] = reset_code
            do_send = True

        if do_send:
            if len(phone) == 9:
                phone = '237' + phone  # This works only for Cameroon
            text = 'Your password reset code is %s' % reset_code
            try:
                main_link = service.config.sms_api_script_url
                if not main_link:
                    main_link = getattr(settings, 'SMS_MAIN_LINK', None)
                send_sms(phone, text, script_url=main_link, fail_silently=False)
            except:
                fallback_link = getattr(settings, 'SMS_FALLBACK_LINK', None)
                send_sms(phone, text, script_url=fallback_link)

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if getattr(settings, 'DEBUG', False):
            self.send_code(request)
        else:
            try:
                self.send_code(request)
            except Member.DoesNotExist:
                error = _('No Member found with this phone number')
                context['error_message'] = error
            except:
                error = _('Could not send code. Please try again later')
                context['error_message'] = error
        return super(SetNewPasswordSMSRecovery, self).get(request, *args, **kwargs)

    def render_to_response(self, context, **response_kwargs):
        response = {'success': True}
        if self.request.GET.get('action') == 'new_code':
            if getattr(settings, 'DEBUG', False):
                self.send_code(self.request, new_code=True)
            else:
                try:
                    self.send_code(self.request, new_code=True)
                except Member.DoesNotExist:
                    error = _('No Member found with this phone number')
                except:
                    response = {'error': _('Could not send code. Please try again later')}
            return HttpResponse(json.dumps(response), 'content-type: text/json', **response_kwargs)
        else:
            return super(SetNewPasswordSMSRecovery, self).render_to_response(context, **response_kwargs)

    @method_decorator(sensitive_post_parameters())
    @method_decorator(never_cache)
    def post(self, request, *args, **kwargs):
        form = SetPasswordFormSMSRecovery(request.POST)
        if form.is_valid():
            reset_code = request.session.get('reset_code')
            if reset_code != form.cleaned_data['reset_code']:
                context = self.get_context_data(**kwargs)
                context['error_message'] = _('Invalid code. Please try again')
                return render(request, self.template_name, context)
            new_pwd1 = form.cleaned_data['new_password1']
            new_pwd2 = form.cleaned_data['new_password2']
            if new_pwd1 != new_pwd2:
                context = self.get_context_data(**kwargs)
                context['error_message'] = _('Passwords mismatch. Please try again')
                return render(request, self.template_name, context)
            phone = request.session['phone']
            active_users = Member.objects.filter(Q(phone=phone) | Q(username=phone))
            for member in active_users:
                # Make sure that no SMS is sent to a user that actually has
                # a password marked as unusable
                if not member.has_usable_password():
                    continue
                member.propagate_password_change(new_pwd1)
            msg = _("Password successfully reset.")
            messages.success(request, msg)
            next_url = reverse('ikwen:sign_in') + '?phone=' + phone
            return HttpResponseRedirect(next_url)
        else:
            context = self.get_context_data(**kwargs)
            context['form'] = form
            return render(request, self.template_name, context)


class AccountSetup(TemplateView):
    template_name= 'accesscontrol/account.html'


@login_required
def update_info(request, *args, **kwargs):
    member = request.user
    form = MemberUpdateForm(request.GET)
    if form.is_valid():
        email = form.cleaned_data.get('email')
        phone = form.cleaned_data.get('phone')
        name = form.cleaned_data.get('name')
        gender = form.cleaned_data.get('gender')
        if email:
            try:
                Member.objects.get(email=email)
                response = {'error': _('This e-mail already exists.')}
                return HttpResponse(json.dumps(response), content_type='application/json')
            except Member.DoesNotExist:
                if member.email != email:
                    member.email_verified = False
                member.email = email
        if phone:
            try:
                Member.objects.get(phone=phone)
                response = {'error': _('This phone already exists.')}
                return HttpResponse(json.dumps(response), content_type='application/json')
            except Member.DoesNotExist:
                if member.phone != phone:
                    member.phone_verified = False
                member.phone = phone
        if name:
            name_tokens = name.split(' ')
            first_name = name_tokens[0]
            last_name = ' '.join(name_tokens[1:])
            member.first_name = first_name
            member.last_name = last_name
        if gender:
            if not member.gender:
                member.gender = gender  # Set gender only if previously not set
        member.save(update_fields=['first_name', 'last_name', 'email', 'phone', 'gender'])
        response = {'message': _('Your information were successfully updated.')}
        return HttpResponse(json.dumps(response), content_type='application/json')
    else:
        return HttpResponse(json.dumps({"error": form.errors}), content_type='application/json')


@login_required
def update_password(request, *args, **kwargs):
    """
    View that changes the password of the user when he intentionally
    decides to do so from his account management panel.
    """
    member = Member.objects.get(pk=request.user.id)
    password = request.GET.get('password')
    if check_password(password, member.password):
        password1 = request.GET.get('password1')
        password2 = request.GET.get('password2')
        response = {'message': _('Your password was successfully updated.')}  # Default is everything going well
        if password1:
            if password1 != password2:
                response = {'error': _("Passwords don't match.")}
            else:
                member.set_password(password1)
                member.save()
                response = {'message': _('Your password was successfully updated.')}
    else:
        response = {'error': _("The current password is incorrect!")}
    return HttpResponse(
        json.dumps(response),
        content_type='application/json'
    )


class Profile(TemplateView):
    template_name = 'accesscontrol/profile.html'

    @method_decorator(cache_page(60 * 5))
    def get(self, request, *args, **kwargs):
        member_id = kwargs['member_id']
        member = get_object_or_404(Member, pk=member_id)
        context = super(Profile, self).get_context_data(**kwargs)
        context['profile_name'] = member.full_name
        context['profile_email'] = member.email
        context['profile_phone'] = member.phone
        context['profile_gender'] = member.gender
        context['profile_photo_url'] = member.photo.small_url if member.photo.name else ''
        context['profile_cover_url'] = member.cover_image.url if member.cover_image.name else ''
        context['member'] = member
        return render(request, self.template_name, context)







