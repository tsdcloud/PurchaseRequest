from django.utils.translation import gettext_lazy as _

SIMPLIFIED = _("SIMPLIFIED")
REAL = _("REAL")
GENERAL = _("GENERAL")
SPECIFIC = _("SPECIFIC")

TAX_REGIMES = (
    ("SIMPLIFIED", SIMPLIFIED),
    ("REAL", REAL),
)

LEVELS = (
    ("CX", "CX"),
    ("HIGH", "HIGH"),
    ("LOW", "LOW"),
    ("MEDIUM", "MEDIUM"),
)

STANDARD_TYPES = (
    ("GENERAL", GENERAL),
    ("SPECIFIC", SPECIFIC),
)