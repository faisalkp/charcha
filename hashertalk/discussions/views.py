from django.shortcuts import render
from django.db.models import F, Count
from django.db.models.functions import Length
from django.contrib.auth.decorators import login_required
from .models import Post, Comment

def homepage(request):
    posts = Post.objects.annotate(
                score=F('upvotes')-F('downvotes')
            ).order_by(
                "submission_time"
            )[:50]

    posts = _secret_sorting(posts)
    return render(request, "home.html", context={"posts": posts})

def _secret_sorting(posts):
    """ Our magic algorithm to sort the posts on homepage """
    return posts

def discussion(request, page):
    post_id = _extract_page_id(page)
    post = Post.objects.get(pk=post_id)
    comments = Comment.objects.filter(post=post)\
                    .annotate(indent = (Length('wbs') + 1)/5 )\
                    .order_by("wbs")
    context = {"post": post, "comments": comments}
    return render(request, "discussion.html", context=context)

def _extract_page_id(page):
    # TODO: Implement SEO friendly URLs 
    # with post id embedded at the end
    return page

@login_required
def submit(request):
    return render(request, "submit.html", context={})

@login_required
def myprofile(request):
    return render(request, "profile.html", context={})

def profile(request, userid):
    return render(request, "submit.html", context={"user": {"id": userid}})

def create_account(request):
    return render(request, "registration/create-account.html", context={})
