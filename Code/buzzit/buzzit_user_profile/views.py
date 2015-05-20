from django.contrib.auth.decorators import login_required
from django.contrib.auth import user_logged_in
from django.core import serializers
from django.http import JsonResponse, HttpResponse
import logging
from buzzit_models.models import Profile


def login_required_json(self):
    if not user_logged_in:
        error = {"error": "login first"}
        return JsonResponse(error)

def get_profile_info(request, username):
    if (request.method == "GET"):
        user = User.objects.all()
        if len(user) < 1:
            logging.getLogger(__name__).error(user)
            error = {"error": "profile " + username + " not found"}
            return JsonResponse(error)
        user.password = "private"
        return JsonResponse(user, safe=False)
    error = {"error": "wrong method - only GET allowed here"}
    return JsonResponse(error)


def update_profile_info(request, username):
    if request.method == "POST":
        user = User.objects.filter(username=username)
        update_str = request.POST.get("update", False)
        if not update_str:
            error = {"error": "no update data given"}
            return JsonResponse(error)
        update = serializers.deserialize('json', update_str)
        for key in update:
            setattr(user, key, update[key])
        updatable_values = ["description", "gender", "first_name", "last_name"]
        user.save(force_update=True, update_fields=updatable_values)
    error = {"error": "wrong method - only POST allowed here"}
    return JsonResponse(error)