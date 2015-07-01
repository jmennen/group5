from django.shortcuts import render
from django.views.generic import ListView
from buzzit_models.models import *
from django.contrib.auth.decorators import login_required
import json

class AdminFrontpageView():
    pass

class UserReportDetailsView(ListView):
    pass


class MessageReportDetailsView(ListView):
    pass


class AdminOverviewView(ListView):
    pass


@login_required
def delete_reported_post(request, message_id):
    pass


@login_required
def promote_user_to_admin(request, user_id):
    pass


@login_required
def demote_admin_to_user(request, user_id):
    pass


@login_required
def report_user(request, user_id):
    pass


@login_required
def report_message(request, message_id):
    pass


@login_required
def ban_user(request, user_id):
    pass