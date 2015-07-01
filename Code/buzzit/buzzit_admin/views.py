from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render
from django.utils.datetime_safe import datetime
from django.utils.decorators import method_decorator
from django.views.generic import ListView, CreateView, DeleteView
from django.http import HttpResponseRedirect, JsonResponse
from buzzit_messaging.views import __send_system__message__
from buzzit_models.models import *
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse, reverse_lazy
import django.contrib.messages as messages

@login_required()
def report_user(request,user_id):
    """
    current user report other user, and gives the reason which would not be empty
    :param request:
    :param user_id:
    :return:
    """

    try:
        reported_user = User.objects.get(pk=user_id)
    except ObjectDoesNotExist:
        messages.error(request,"Der Benutzer existiert nicht.")
        return HttpResponseRedirect(reverse_lazy("home"))
    if request.method == "POST":
        report_text = request.POST.get["text"]
        if not report_text:
            render(request,"home",{"error: Zum Benutzermelden ist Meldungstext notwendig."})
    report_message = Report(creator=request.user,created=datetime.now(),text=report_text)
    report_message.save()
    messages.INFO("Sie haben den <User:%s> Benutzer gemeldet" %reported_user)

    #send notifacations to system users
    system_user = User.objects.get(username="SYSTEM")
    __send_system__message__(system_user.pk, "<Report:%s> Neue Meldung " % report_message)

    return HttpResponseRedirect(reverse_lazy('home'))

@login_required()
def report_user_details():
    pass

class UserReportDetailsView(ListView):
    pass

@login_required
def delete_reported_post(request, message_id):
    pass

@login_required
def report_message(request, message_id):
    pass
