from django.utils.translation import gettext_lazy as _

GOODS = "GOOD"
SERVICE = "SERVICE"
PURCHASE_REQUEST_TYPES = (
    (GOODS, _("GOODS")),
    (SERVICE, _("SERVICE"))
)
