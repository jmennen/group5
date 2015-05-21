from django.http import JsonResponse
from buzzit_models.models import Profile
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.forms.models import model_to_dict

def get_profile_info(request, username):
    """
    GET the requested profile.
    The user is also returned instead of only a foreign key, but some fields are excluded:
    excluded = ["password", "user_permissions", "groups", "email"]
    Args:
        request: the http request
        username: the username being requested
    Return:
        JSON response in two ways
        1.  {"ok" : False, "error" : "<error message>"} if any error occured
        2.  {"ok" : True, "profile" :   {
                                            <profile object>,
                                            ...,
                                            "user" : <user object without excluded fields>,
                                            ...
                                        }
            }
    """
    if not request.user.is_authenticated():
        error = {"ok": False, "error": "login first"}
        return JsonResponse(error)
    if (request.method == "GET"):
        try:
            user = User.objects.get(username=username)
        except ObjectDoesNotExist:
            error = {"ok": False, "error": "user " + username + " not found"}
            return JsonResponse(error)
        try:
            profile_obj = Profile.objects.get(user=user)
        except ObjectDoesNotExist:
            error = {"ok": False, "error": "profile " + username + " not found"}
            return JsonResponse(error)
        profile_dict = model_to_dict(profile_obj)
        user_dict = model_to_dict(user, exclude=["password", "user_permissions", "groups", "email"])
        profile_dict["user"] = user_dict
        ret = {"ok": True, "profile": profile_dict}
        return JsonResponse(ret, content_type="application/json")
    error = {"ok": False, "error": "wrong method - only GET allowed here"}
    return JsonResponse(error)


def update_profile_info(request):
    """
    UPDATE the profile. This contains the possibility to update the profile description and gender.
    Args:
        request: the http request
    Return:
        JSON response in two ways
        1. {"ok" : False, "error" : "<error message>"} if any error occured
        2. {"ok" : True, "info" : {"updated" : <updated keys as array>, "ignored" : <ignored keys>}}
    """
    if not request.user.is_authenticated():
        error = {"ok": False, "error": "login first"}
    if request.method == "POST":
        if not request.POST:
            error = {"ok": False, "error": "no update data given", "post": request.POST}
            return JsonResponse(error)
        user = request.user;
        profile = Profile.objects.filter(user=user)[0]
        updatable_values = ["description", "gender"]
        info = {"updated": [], "ignored": []}
        for key in request.POST:
            if key in updatable_values:
                info["updated"].append(key)
                setattr(profile, key, request.POST[key])
            else:
                info["ignored"].append(key)
        profile.save(force_update=True)
        return JsonResponse({"ok": True, "info": info})
    error = {"ok": False, "error": "wrong method - only POST allowed here"}
    return JsonResponse(error)