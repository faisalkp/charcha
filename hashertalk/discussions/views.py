from django.http import HttpResponse, HttpResponseRedirect
from django.views import View 
from django.views.decorators.http import require_http_methods
from django import forms
from django.shortcuts import render, get_object_or_404
from django.db.models import F, Count
from django.db.models.functions import Length
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.contenttypes.models import ContentType

from .models import Post, Comment, Vote
from .models import UPVOTE, DOWNVOTE, FLAG, UNFLAG

def homepage(request):
    posts = Post.objects\
                .select_related("author")\
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
@require_http_methods(['POST'])
def upvote_post(request, post_id):
    new_score, flags = _vote_on_post(request, post_id, UPVOTE)
    return HttpResponse(new_score)

@login_required
@require_http_methods(['POST'])
def downvote_post(request, post_id):
    new_score, flags = _vote_on_post(request, post_id, DOWNVOTE)
    return HttpResponse(new_score)

@login_required
@require_http_methods(['POST'])
def flag_post(request, post_id):
    new_score, flags = _vote_on_post(request, post_id, FLAG)
    return HttpResponse('unflag')

@login_required
@require_http_methods(['POST'])
def unflag_post(request, post_id):
    new_score, flags = _vote_on_post(request, post_id, UNFLAG)
    return HttpResponse('flag')

def _vote_on_post(request, post_id, type_of_vote):
    post = get_object_or_404(Post, pk=post_id)

    if _already_voted(request.user, post, type_of_vote):
        print("User already voted, ignoring")
        return post.score, post.flags

    # First, save the vote
    vote = Vote(content_object=post, voter=request.user, type_of_vote=type_of_vote)
    vote.save()

    # Next, update our denormalized columns - flags and score
    if type_of_vote == FLAG:
        post.flags = F('flags') + 1
    elif type_of_vote == UNFLAG:
        post.flags = F('flags') - 1 
    elif type_of_vote == UPVOTE:
        post.score = F('score') + 1
    elif type_of_vote == DOWNVOTE:
        post.score = F('score') - 1
    else:
        raise Exception("Invalid type of vote " + type_of_vote)
    post.save()

    # Finally, return either the updated score or the updated flags
    post = Post.objects.only('score', 'flags').get(pk=post_id)
    return post.score, post.flags

def _already_voted(user, post, type_of_vote):
    # TODO: can we cache post_type?
    post_type = ContentType.objects.get_for_model(post)
    return Vote.objects.filter(content_type=post_type.id,
                object_id=post.id,\
                voter=user, type_of_vote=type_of_vote)\
            .exists()

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
