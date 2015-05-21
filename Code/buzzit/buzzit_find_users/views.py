from django.http import JsonResponse


def find_users(request, username):
    if not request.user.is_authenticated():
        error = {"ok": False, "error": "login first"}
        return JsonResponse(error)
    if request.method == "POST":

        return JsonResponse({"ok" : False, "error" : "not implemented now"})
    error = {"ok": False, "error": "wrong method - only POST allowed here"}
    return JsonResponse(error)