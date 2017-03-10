from django.shortcuts import render
from django.db.models import Count
from .models import Post
from django.contrib.auth.decorators import login_required

def homepage(request):
    posts = Post.objects.raw("""
        SELECT p.id, p.title, p.url, p.text, p.author_id, 
        author.username as username, p.submission_time, 
        coalesce(c.num_comments, 0) as num_comments, 
        coalesce(up.votes, 0) as upvotes, 
        coalesce(down.votes, 0) as downvotes
        FROM posts p
        INNER JOIN auth_user author on p.author_id = author.id
        LEFT OUTER JOIN (
                SELECT c1.post_id as post_id, count(*) as num_comments 
                FROM comments c1
                GROUP BY c1.post_id) c 
            on p.id = c.post_id
        LEFT OUTER JOIN (
                SELECT u1.object_id as post_id, count(*) as votes 
                FROM votes u1
                WHERE u1.type_of_vote = 1
                GROUP BY u1.object_id) up
            on p.id = up.post_id
        LEFT OUTER JOIN (
                SELECT d1.object_id as post_id, count(*) as votes 
                FROM votes d1
                WHERE d1.type_of_vote = 2
                GROUP BY d1.object_id) down
            on p.id = down.post_id
        ORDER BY p.submission_time desc
        LIMIT 20
        """)
    return render(request, "home.html", context={"posts": posts})
    
def discussion(request, page):
    return render(request, "discussion.html", context={"page": page})

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
