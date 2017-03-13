from django.http import HttpResponse, HttpResponseRedirect
from django.views import View 
from django import forms
from django.shortcuts import render
from django.db.models import F, Count
from django.db.models.functions import Length
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Post, Comment

def homepage(request):
    posts = Post.objects.annotate(score=F('upvotes')-F('downvotes'))\
                        .order_by("submission_time")[:50]
    return render(request, "home.html", context={"posts": posts})

def discussion(request, post_id):
    post = Post.objects.get(pk=post_id)
    comments = Comment.objects.filter(post=post)\
                    .annotate(indent = (Length('wbs') + 1)/5 )\
                    .order_by("wbs")
    context = {"post": post, "comments": comments}
    return render(request, "discussion.html", context=context)

@login_required
def submit(request):
    return render(request, "submit.html", context={})

@login_required
def myprofile(request):
    return render(request, "profile.html", context={})

class CreateProfileView(View):
    def post(self, request):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return HttpResponseRedirect('/')
        else:
            return render(request, "registration/create-account.html", {"form": form})

    def get(self, request):
        form = UserCreationForm()
        return render(request, "registration/create-account.html", {"form": form})

def profile(request, userid):
    return render(request, "profile.html", context={"user": {"id": userid}})
