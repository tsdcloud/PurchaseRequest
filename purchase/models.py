from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import JSONField
from django.http import HttpResponse, Http404
from django.utils.translation import gettext_lazy as _

from commons.constants import PURCHASE_REQUEST_TYPES
from commons.models import Model, BaseUUIDModel, Member
from purchase.constants import TAX_REGIMES, LEVELS, STANDARD_TYPES


class Standard(Model):
    name = models.CharField(max_length=150)
    certified_company = models.CharField(_("Certify company"), max_length=150, blank=True, null=True)
    type = models.CharField(max_length=150, choices=STANDARD_TYPES)
    standard_name = models.CharField(max_length=150, blank=True, null=True)


class Category(Model):
    name = models.CharField(max_length=150)
    level = models.CharField(max_length=10, choices=LEVELS)


class Product(Model):
    name = models.CharField(max_length=150)
    brand = models.CharField(_("Brand"), max_length=150, null=True)
    stock = models.IntegerField(_("Stock"), default=0, help_text=_("Quantity of the product"))
    unit_of_measurement = models.CharField(_("Unit of measurement"), max_length=60, blank=True, null=True,
                                           help_text=_("Unit of measurement for this product."))
    description = models.TextField()
    release_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    unit_prize = models.FloatField(db_index=True, default=0)

    # def save(
    #     self, force_insert=False, force_update=False, using=None, update_fields=None
    # ):
    #     if self.expiry_date and self.release_date:
    #         if self.expiry_date < self.release_date:
    #             raise HttpResponse("")


class ProvisionRequest(Model):
    code = models.CharField(max_length=150, unique=True)
    applicant = models.ForeignKey(Member, on_delete=models.SET_NULL)
    products = models.ManyToManyField('purchase.Product', through="ProvisionProductEntry", null=True)





class ProvisionProductEntry(Model):
    provision_request = models.ForeignKey(ProvisionRequest, on_delete=models.CASCADE)
    product = models.ForeignKey('purchase.Product', on_delete=models.CASCADE)
    applicant = models.ForeignKey(Member, blank=True, null=True, on_delete=models.SET_NULL)
    product_cost = models.FloatField(db_index=True, null=True)  # Cost of product at the moment the Order is issued
    count = models.IntegerField(db_index=True, null=True)

    class Meta:
        unique_together = ('provision_request', 'product')

    def get_total(self):
        """Gets the total cost for this entry only. Mainly aimed at usage in django templates"""
        return self.product_cost * self.count


class Purchase(Model):
    purchase_type = models.CharField(max_length=10, choices=PURCHASE_REQUEST_TYPES)
    delivery_delay = models.DateTimeField() 


class Provider(Model):
    name = models.CharField(max_length=150, unique=True)
    acronym = models.CharField(max_length=10, null=True, blank=True)
    activity_list = JSONField()
    phone_1 = models.CharField(max_length=9, blank=True, null=True)
    phone_2 = models.CharField(max_length=9, blank=True, null=True)
    email = models.EmailField(null=True, blank=True)
    tax_regime = models.CharField(max_length=10, choices=TAX_REGIMES)
    legal_status_acronym = models.CharField(max_length=150)
    standards = models.ManyToManyField(Standard)
    categories = models.ManyToManyField(Category)
    service = models.CharField(max_length=200)


class OrderForm(Model):
    code = models.CharField(max_length=150, unique=True)


class ExitVoucher(Model):
    pass




