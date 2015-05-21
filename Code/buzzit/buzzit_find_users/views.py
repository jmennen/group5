from django.http import JsonResponse
from django.contrib.auth.models import User
from django.forms.models import model_to_dict


def find_users(request, username):
    """
    GET the users, whose username contains <username>
    excluded = ["password", "user_permissions", "groups", "email"]
    Args:
        request: the http request
        username: the (part of the) username of users to find
    Return:
        JSON response in two ways
        1.  {"ok" : False, "error" : "<error message>"} if any error occured
        2.  {"ok" : True, "users" :   [
                                            <user object without excluded fields>
                                        ]
            }
    """
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