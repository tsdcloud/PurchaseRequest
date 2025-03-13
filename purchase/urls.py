from django.urls import path

from purchase.views import *

app_name = 'purchase'

urlpatterns = [
    path('', provision_request, name='provision_request'),
    path('save_parent_session_list', save_parent_session_list, name='save_parent_session_list'),
    path('accept_parent_invitation', accept_parent_invitation, name='accept_parent_invitation'),
    path('rate_teacher', rate_teacher, name='rate_teacher'),
    path('assignments', kid_assignments, name='kid_assignments'),
    path('assignments/<pk>', kid_assignments, name='kid_assignments'),
    path('score_summary/', score_summary, name='score_summary'),
]
