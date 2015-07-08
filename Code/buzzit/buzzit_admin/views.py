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
from django.views.generic import ListView, DetailView
from buzzit_models.models import *
from django.contrib.auth.decorators import login_required
import json
from django.core.mail import send_mail

@login_required()
def report_user(request,user_id):
    """
    current user report other user, and gives the reason which should not be empty
    :param request:
    :param user_id:
    :return:
    """
    if request.method == "POST":
        try:
            reported_user = User.objects.get(pk=user_id)
        except ObjectDoesNotExist:
            messages.error(request,"Der Benutzer existiert nicht.")
            return HttpResponseRedirect(reverse_lazy("home"))
        if request.method == "POST":
            report_message = UserReport()
            report_text = request.POST.get["text",False]
            try:
                if report_text:
                    report_message.text=report_text
            except ObjectDoesNotExist:
                messages.error(request,"Fehler")

            if len(report_message.text) < 1:
                messages.error(request,"Text zum Benutzermelden ist zu geben")
                return HttpResponseRedirect(reverse_lazy("home"))

            report_message.creator=request.user
            report_message.created=datetime.now()
            report_message.reported_user=reported_user
            report_message.save()
            messages.info("Sie haben den <User:%s> Benutzer gemeldet" %reported_user)

            #TODO send messages to admin user, not to SYSTEM user
            admin_user = User.objects.filter(is_staff=True)
            __send_system__message__(admin_user.pk, "<Report:%s> Neue Meldung " % report_message)

            return HttpResponseRedirect(reverse_lazy('home'))
    else:
        try:
            reported_profile = Profile.objects.get(pk=user_id)
        except ObjectDoesNotExist:
            messages.error(request,"Der Benutzer existiert nicht.")
            return HttpResponseRedirect(reverse_lazy("home"))
        return render(request, "logged_in/report_user.html", {"profile":reported_profile})

class UserReportDetailsView(SuccessMessageMixin,ListView):
    """
    display the report text and reported user
    """
    model = UserReport
    template_name = "logged_in/user_report_deatails"

    def get_queryset(self):
        try:
            reported_user = self.kwargs.get["user_id"]
        except ObjectDoesNotExist:
            messages.error(self.request,"Benutzer existiert nicht")
            return HttpResponseRedirect(reverse_lazy("admin_frontpage"))
        return UserReport.objects.filter(reported_user=reported_user).order_by("created").all()

    def get_context_data(self, **kwargs):
        try:
            reported_user=self.kwargs.get["user_id"]
        except ObjectDoesNotExist:
            messages.error(self.request,"Benutzer existiert nicht")
            return HttpResponseRedirect(reverse_lazy("admin_frontpage"))

        reported_user_profile = reported_user.profile
        report = UserReport.objects.get(reported_user=reported_user)
        context=super(UserReportDetailsView, self).get_context_data(**kwargs)
        context["reported_user_profile"]= reported_user_profile
        context["report_text"]=report.text

        return context

    def dispatch(self, request, *args, **kwargs):
        return super(UserReportDetailsView, self).dispatch(request,*args,**kwargs)

class AdminFrontpageView():
    pass
	
@login_required
def adminFrontPage(request):
     """
     show all userreports and
     postreports
     :param request:
     :return:
     """
     if request.user.is_superuser:
        userreports =[]
        postreports=[]
        userreports = UserReport.objects.all()
        postreports =CircleMessageReport.objects.all()

        return render(request,"logged_in/admin_dashboard.html",{"user_reports":userreports,"post_reports":postreports})
     else:
         messages.error(request, "Sie haben nicht die nötigen Zugangsrechte!")
         return HttpResponseRedirect(reverse("home"))


class MessageReportDetailsView(DetailView):
    model = CircleMessageReport
    slug_field = "id"
    template_name = "logged_in/post_report_details.html"

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(MessageReportDetailsView, self).dispatch(request, args, kwargs)


class AdminOverviewView(ListView):
    pass

@login_required
def delete_reported_post(request, report_id):
    """
    delete reported message from admin, check if the message has answers,
    reported message with all answers would be delete, else delete only message
    TODO was ist, wenn eine Nachricht rebuzzed wurde
    :param request:
    :param message_id:
    :return:
    """
    try:
        report = CircleMessageReport.objects.get(pk = report_id)
    except ObjectDoesNotExist:
        messages.error(request,"Der Report existiert nicht")
        return HttpResponseRedirect(reverse_lazy("admin_frontpage"))

    if not(request.user.is_superuser):
        messages.error(request, "Sie haben nicht die nötigen Zugangsrechte!")
        return HttpResponseRedirect(reverse("home"))
    
    #if the reported post has anwsers, delete all

    post_to_del=report.reported_message
    answers=Circle_message.objects.filter(answer_to=post_to_del)
    answers.delete()
    post_to_del.delete()
    report.issuer = request.user
    report.valid = True
    report.closed = True
    messages.success(request,"Die Nachrichte wurde erfolgreich geloescht")
    return HttpResponseRedirect(reverse_lazy("admin_frontpage"))

@login_required
def dismiss_report(request, report_id):
    try:
        report = CircleMessageReport.objects.get(pk = report_id)
    except ObjectDoesNotExist:
        messages.error(request,"Der Report existiert nicht")
        return HttpResponseRedirect(reverse_lazy("admin_frontpage"))
    
    if not(request.user.is_superuser):
        messages.error(request, "Sie haben nicht die nötigen Zugangsrechte!")
        return HttpResponseRedirect(reverse("home"))
    
    post_to_del=report.reported_message
    report.issuer = request.user
    report.valid = False
    report.closed = True
    messages.success(request,"Der Report wurde erfolgreich bearbeitet")
    return HttpResponseRedirect(reverse_lazy("admin_frontpage"))


@login_required
def promote_user_to_admin(request, user_id):
    """
    check if user exists, then check if user is active
    :param request:
    :param user_id:
    :return:
    """
    try:
        admin_user=User.objects.get(pk=user_id)
    except ObjectDoesNotExist:
        messages.error(request,"Der Benuzer existiert nicht")
        return HttpResponseRedirect(reverse_lazy("admin_frontpage"))

    if not(admin_user.is_active):
        messages.info(request,"Der Benutzer ist deaktiviert")
        return HttpResponseRedirect(reverse_lazy("admin_frontpage"))

    admin_user.is_staff=True
    messages.info(request,"Der Benutzer ist als AdminUser hinzugefuegt")
    return HttpResponseRedirect(reverse_lazy("admin_frontpage"))

@login_required
def demote_admin_to_user(request, user_id):
    """
    check if user exists, check if user is adminUser
    :param request:
    :param user_id:
    :return:
    """
    try:
        demote_user=User.objects.get(pk=user_id)
    except ObjectDoesNotExist:
        messages.error(request,"Der Benutzer existiert nicht")
        return HttpResponseRedirect(reverse_lazy("admin_frontpage"))

    if not(demote_user.is_staff):
        messages.error(request,"Der Benutzer ist kein Admin ")
        return HttpResponseRedirect(reverse_lazy("admin_frontpage"))

    demote_user.is_staff=False
    messages.info(request,"Die Adminrechte von dem Benutzer wird entziehen")
    return HttpResponseRedirect(reverse_lazy("admin_frontpage"))

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
        reported_message = Circle_message.objects.get(pk=message_id)
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
    reported_profile = Profile.objects.get(pk = reported_message.creator.pk)
    return render(request, "logged_in/report_post.html", {"profile" : reported_profile, "circlemessage" : reported_message})

@login_required
def ban_user(request, user_id):
    """
    set ban user and send email to him with reason,TODO provides ban user information to contact with admin user
    :param request:
    :param user_id:
    :return:
    """
    try:
        user_to_be_ban=User.objects.get(pk=user_id)
    except ObjectDoesNotExist:
        messages.error(request,"Der Benutzer existiert nicht")
        return HttpResponseRedirect(reverse_lazy("admin_frontpage"))

    if not(user_to_be_ban.is_active):
        messages.info(request,"Der Benutzer ist bereits deaktiviert")
        return HttpResponseRedirect(reverse_lazy("admin_frontpage"))

    message_for_ban=request.GET.get["text",False]
    user_to_be_ban.is_active=False
    send_mail("Deaktivieren dein Account", message= "Grund zum Deaktivieren: '%s'" % message_for_ban,
                      html_message="<html><h3>um Deinen Account zu wieder aktivieren, kontaktieren Sie bitte :</h3>" +
                                   "<a href='%s'>Klicke hier um den Account wieder zu aktivieren!</a>."  +
                                   "</html>" ,from_email="AccountAktivierung@vps146949.ovh.net", recipient_list=(user_to_be_ban.email,))
    messages.info(request,"Der Benutzer ist deaktiviert")
    return HttpResponseRedirect(reverse_lazy("admin_frontpage"))
