from django.conf import settings
from django.contrib.auth.decorators import permission_required

from django.contrib.auth.models import Permission
from django.contrib.auth.models import Group

from rest_framework import serializers

from commons.models import *
from commons.permissions import *


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ["name", "permission"]
