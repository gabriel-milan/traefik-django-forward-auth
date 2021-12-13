from django.contrib.auth import logout, login, authenticate
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render, redirect

from .utils import (
    get_redirect_uri,
    get_public_uri,
)


def auth(request: HttpRequest):
    if request.user.is_authenticated:
        return HttpResponse("OK")
    else:
        redirect_uri = get_redirect_uri(request)
        if redirect_uri:
            return redirect(f"{get_public_uri()}/auth/login/?redirect={redirect_uri}")
        return redirect(f"{get_public_uri()}/auth/login/")


def signin(request: HttpRequest):
    redirect_uri = get_redirect_uri(request, default="/")
    if request.user.is_authenticated:
        return redirect(redirect_uri)
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            response: HttpResponse = redirect(redirect_uri)
            return response
        else:
            return HttpResponse('Invalid login')
    return render(request, 'login.html')


def signout(request: HttpRequest):
    if request.user.is_authenticated:
        logout(request)
        redirect_uri = get_redirect_uri(request, default="/")
        return redirect(redirect_uri)
    else:
        return HttpResponse("You are not logged in")
