from django.http import JsonResponse
from django.contrib.auth.models import User


def find_users(request, username):
    if not request.user.is_authenticated():
        error = {"ok": False, "error": "login first"}
        return JsonResponse(error)
    if request.method == "GET":
        users = User.objects.filter(username__like=username)
        return JsonResponse({"ok" : True, "users" : users})
    error = {"ok": False, "error": "wrong method - only GET allowed here"}
    return JsonResponse(error)