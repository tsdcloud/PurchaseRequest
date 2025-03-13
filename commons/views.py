# Create your views here.
import json
import os
import uuid
from datetime import datetime, timedelta
from threading import Thread

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q, F, Sum
from django.dispatch import receiver
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
from django.http import HttpResponseBadRequest, HttpResponse, Http404, QueryDict
from django.urls import reverse
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

from commons.serializers import GroupSerializer
from commons.utils import BearerAuthentication


# from rest_framework.decorators import detail_route


class GroupViewSet(viewsets.ModelViewSet):
    """
        API endpoint that allows groups management.
        """
    queryset = Group.objects.all().order_by("-id")
    serializer_class = GroupSerializer
    authentication_classes = [BearerAuthentication]
    permission_classes = [permissions.IsAdminUser]

    @action(detail=False, methods=['PATCH'])
    def grant_permission(self, request):
        # Obtenir le nom de la permission depuis les données de la requête
        permission_name = request.data.get('permission_name')
        # Obtenir le code de permission depuis les données de la requête
        permission_code = request.data.get('permission_code')
        group = self.get_object()

        try:
            # Récupérer l'objet permission à partir du copermission_code
            permission = Permission.objects.get(codename=permission_code)

            # Ajouter la permission à un groupe
            group.permissions.add(permission)

            if group.has_perm(permission):
                return Response({"message": "Group already has that permission"}, status=status.HTTP_404_NOT_FOUND)
            # Code de succès avec un message de réussite
            return Response({'message': f"La permission {permission_name} a été attribuée au groupe {group.name}."})

        except Group.DoesNotExist:
            # Gérer l'erreur si l'utilisateur n'existe pas
            return Response({'message': 'L\'utilisateur spécifié n\'existe pas.'}, status=status.HTTP_404_NOT_FOUND)

        except Permission.DoesNotExist:
            # Gérer l'erreur si la permission n'existe pas
            return Response({'message': 'La permission spécifiée n\'existe pas.'}, status=status.HTTP_404_NOT_FOUND)


class Login(APIView):
    def post(self, request, format=None):
        #try:
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        try:
            # Delete user token if it hasn't been deleted when he logged out
            Token.objects.get(user=user).delete()
        except:
            pass
        token = Token.objects.create(user=user)
        return Response({"success": True, "message": f"{user.get_full_name()} logged in successfully", "user": AgentSerializer(user).data, "token": token.key}, status=status.HTTP_200_OK)
#        except Exception as e:
#            return Response("Authentication failed", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class Logout(APIView):
    authentication_classes = [BearerAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, format=None):
        try:
            # simply delete the token to force a login
            request.user.auth_token.delete()
            # Profile.objects.filter(member_id=self.request.user.id).delete()
            return Response("User Logged out successfully /205/ ", status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response("BAD REQUEST /400/ ", status=status.HTTP_400_BAD_REQUEST)


@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    """
        Handles password reset tokens
        When a token is created, an e-mail needs to be sent to the user
        :param sender: View Class that sent the signal
        :param instance: View Instance that sent the signal
        :param reset_password_token: Token Model Object
        :param args:
        :param kwargs:
        :return:
    """
    subject = _("Reset your password")
    project_name = getattr(settings, "PROJECT_NAME", "EasyPro")
    # domain = getattr(settings, "DOMAIN", "easyproonline.com")
    domain = getattr(settings, "DOMAIN", "easyproonline.com")
    # sender = getattr(settings, "EMAIL_HOST_USER", '%s <no-reply@%s>' % (project_name, domain))
    sender = 'contact@africadigitalxperts.com'
    # send an e-mail to the user
    context = {
        'company_name': "EASYPRO",
        'service_url': domain,
        # 'logo_url': "https://rh_support.dpws.bfc.cam/images/bfc_logo.png",
        'current_user': reset_password_token.user,
        'username': reset_password_token.user.username,
        'email': reset_password_token.user.email,
        'reset_password_url': "{}?token={}".format(
            instance.request.build_absolute_uri(reverse('password_reset:reset-password-confirm')),
            reset_password_token.key),
        'protocol': 'http',
        'domain': domain
    }
    template_name = "mails/password_reset_email.html"
    html_template = get_template(template_name)
    # render email text
    html_content = html_template.render(context)
    msg = EmailMessage(subject, html_content, sender, [reset_password_token.user.email],
                       bcc=['axel.deffo@gmail.com', 'alexis.k.abosson@hotmail.com', 'silatchomsiaka@gmail.com',
                            'sergemballa@yahoo.fr', 'imveng@yahoo.fr'])
    msg.content_subtype = "html"
    if getattr(settings, 'UNIT_TESTING', False):
        msg.send()
    else:
        Thread(target=lambda m: m.send(), args=(msg, )).start()


class ChangePasswordView(UpdateAPIView):
    """
    This endpoint intend to change user's password.
    """
    serializer_class = ChangePasswordSerializer
    model = Agent
    permission_classes = (IsAuthenticated, IsAdminUser)
    authentication_classes = [BearerAuthentication]

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    @action(detail=True, methods=['PATCH'])
    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)
        print(serializer)

        if serializer.is_valid():
            if serializer.data.get("new_password") != serializer.data.get("confirmed_password"):
                return Response({"new_password": _("Password mismatched")}, status=status.HTTP_409_CONFLICT)
            # Check old password
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
            # set_password also hashes the password that the user will get
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            response = {
                'status': 'success',
                'code': status.HTTP_200_OK,
                'message': 'Password updated successfully',
                'data': []
            }
            # # Set Admin user's token to no expiring date
            # if TokenUser.is_superuser:
            #     exp = datetime.now() + timedelta(days=365)
            #     OutstandingToken.objects.filter(user=TokenUser.id).update(expires_at=exp)

            return Response(response)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)