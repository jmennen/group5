from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render
from django.utils.datetime_safe import datetime
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from django.http import HttpResponseRedirect, JsonResponse
from buzzit_messaging.views import __send_system__message__
from buzzit_models.models import *
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse, reverse_lazy
import django.contrib.messages as messages
from django.views.generic import ListView
from buzzit_models.models import *
from django.contrib.auth.decorators import login_required
import json

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

    # send notifications to system users
    system_user = User.objects.get(username="SYSTEM")
    __send_system__message__(system_user.pk, "<Report:%s> Neue Meldung " % report_message)

    return HttpResponseRedirect(reverse_lazy('home'))

class UserReportDetailsView(SuccessMessageMixin,ListView):
    """
    display the report text and reported user
    """
    model = Report
    template_name = "logged_in/user_report_deatails"
    context_object_name = "all_reports"

    def get_queryset(self):
        pass

    def get_context_data(self, **kwargs):
        pass

		
class AdminFrontpageView():
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
def report_message(request, message_id):
    """
    Report a circlemessage with given <message_id>, if that exists.
    If that does not exist, then an error for the user is returned and he gets redirected to home.
    If that message exists,
        then the report will be created, if an reason (report.text) was given.
            The report is saved then.
        if there is no reason, an error will be created and the user is redirected to home.
    :param request:
    :param message_id:
    :return:
    """
    try:
        reported_message = Circle_message(pk=message_id)
    except Exception:
        messages.error(request, "Die Nachricht existiert nicht")
        return HttpResponseRedirect(reverse("home"))
    if request.method == "POST":
        report = CircleMessageReport()
        report.reported_message = reported_message
        report.text = request.POST.get("text", False)
        if not report.text or len(report.text)<1:
            messages.error(request, "Keine Begruendung angegeben")
            return HttpResponseRedirect(reverse("home"))
        report.creator = request.user
        report.created = datetime.now()
        report.save()
        messages.success(request, "Nachricht wurde gemeldet")
        return HttpResponseRedirect(reverse("home"))
    return render(request, "logged_in/report_user.html", {"message" : reported_message})


@login_required
def ban_user(request, user_id):
    pass
