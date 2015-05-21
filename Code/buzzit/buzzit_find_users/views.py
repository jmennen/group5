from django.http import JsonResponse
from django.contrib.auth.models import User
from django.forms.models import model_to_dict


def find_users(request, username):
    if not request.user.is_authenticated():
        error = {"ok": False, "error": "login first"}
        return JsonResponse(error)
    if request.method == "GET":
        users = User.objects.filter(username__contains=username)
        users_arr = []
        for user in users:
            users_arr.append(model_to_dict(user, exclude=["password", "user_permissions", "groups", "email"]))
        return JsonResponse({"ok": True, "users": users_arr})
    error = {"ok": False, "error": "wrong method - only GET allowed here"}
    return JsonResponse(error)