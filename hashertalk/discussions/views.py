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

from django.forms.models import model_to_dict
from django.urls import reverse

from .models import Post, Comment, Vote
from .models import UPVOTE, DOWNVOTE, FLAG, UNFLAG

from collections import defaultdict

def homepage(request):
    posts = Post.objects\
                .select_related("author")\
                .order_by("-submission_time")[:50]
    
    if request.user.is_authenticated():
        posts = _append_votes_by_user(posts, request.user)

    return render(request, "home.html", context={"posts": posts})

def _append_votes_by_user(posts, user):
    # Returns a dictionary
    # key = postid
    # value = set of votes cast by this user
    # for example set('downvote', 'flag')
    post_ids = [p.id for p in posts]
    post_type = ContentType.objects.get_for_model(Post)
    objects = Vote.objects.\
                only('object_id', 'type_of_vote').\
                filter(content_type=post_type.id,
                    object_id__in=post_ids,
                    voter=user)

    votes_by_post = defaultdict(set)
    for obj in objects:
        vote_type_str = _vote_type_to_string(obj.type_of_vote)
        votes_by_post[obj.object_id].add(vote_type_str)

    posts_as_list = []
    for p in posts:
        post = model_to_dict(p)
        post['submission_time'] = p.submission_time
        post['author'] = p.author.username
        post['votes'] = votes_by_post[p.id]
        posts_as_list.append(post)
    return posts_as_list

def _vote_type_to_string(vote_type):
    mapping = {
        UPVOTE: "upvote",
        DOWNVOTE: "downvote",
        FLAG: "flag",
        UNFLAG: "unflag"
    }
    return mapping[vote_type]

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        labels = {
            'text': 'Your Comment',
        }

class DiscussionView(View):
    def get(self, request, post_id):
        post = Post.objects.select_related("author").get(pk=post_id)
        comments = Comment.objects.filter(post=post)\
                        .select_related("author")\
                        .annotate(indent = (Length('wbs') + 1)/5 )\
                        .order_by("wbs")
        form = CommentForm()
        context = {"post": post, "comments": comments, "form": form}
        return render(request, "discussion.html", context=context)

    def post(self, request, post_id):
        post = Post.objects.select_related("author").get(pk=post_id)
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment = _add_comment(comment, post, None, request.user)
            post_url = reverse('discussion', args=[post.id])
            return HttpResponseRedirect(post_url)
        else:
            context = {"post": post, "form": form, "comments": []}
            return render(request, "discussion.html", context=context)

class ReplyToComment(View):
    def get(self, request, **kwargs):
        parent_comment = get_object_or_404(Comment, pk=kwargs['id'])
        post = parent_comment.post
        form = CommentForm()
        context = {"post": post, "parent_comment": parent_comment, "form": form}
        return render(request, "reply-to-comment.html", context=context)

    def post(self, request, **kwargs):
        parent_comment = get_object_or_404(Comment, pk=kwargs['id'])
        post = parent_comment.post
        form = CommentForm(request.POST)
        context = {"post": post, "parent_comment": parent_comment, "form": form}
        
        if not form.is_valid():
            return render(request, "reply-to-comment.html", context=context)

        comment = form.save(commit=False)
        comment = _add_comment(comment, post, parent_comment, request.user)

        post_url = reverse('discussion', args=[post.id])
        return HttpResponseRedirect(post_url)

def _add_comment(comment, post, parent_comment, author):
    comment.post = post
    if parent_comment:
        comment.parent_comment = parent_comment
        comment.wbs = _find_next_wbs(post, parent_wbs=parent_comment.wbs)
    else:
        comment.wbs = _find_next_wbs(post)
    comment.author = author
    comment.save()
    return comment

def _find_next_wbs(post, parent_wbs=None):
    if parent_wbs:
        comments = Comment.objects.raw("""
            SELECT id, max(wbs) as wbs from comments 
            WHERE post_id = %s and wbs like %s
            and length(wbs) = %s
            ORDER BY wbs desc
            limit 1
            """, [post.id, parent_wbs + ".%", len(parent_wbs) + 5])
    else:
        comments = Comment.objects.raw("""
            SELECT id, max(wbs) as wbs from comments 
            WHERE post_id = %s
            and length(wbs) = %s
            ORDER BY wbs desc
            limit 1
            """, [post.id, 4])

    comment = None
    for c in comments:
        comment = c

    if not comment:
        return "%s.%s" % (parent_wbs, "0000")
    elif not comment.wbs:
        return "%s.%s" % (parent_wbs, "0000")
    else:
        wbs_code = comment.wbs
        first_wbs = wbs_code[:-4]
        last_wbs = wbs_code.split(".")[-1]
        next_wbs = int(last_wbs) + 1
        return first_wbs + '{0:04d}'.format(next_wbs)

class StartDiscussionForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'text']
        labels = {
            'title': 'Title',
            'text': 'Details'
        }
        help_text = {
            'title': 'Title',
            'text': 'Markdown syntax allowed'
        }

    def clean(self):
        cleaned_data = super(StartDiscussionForm, self).clean()
        url = cleaned_data.get("url")
        text = cleaned_data.get("text")
        if not (url or text):
            raise forms.ValidationError(
                "URL and Text are both empty. Please enter at least one of them."
            )
        return cleaned_data

class StartDiscussionView(View):
    def get(self, request):
        form = StartDiscussionForm(initial={"author": request.user})
        return render(request, "submit.html", context={"form": form})

    def post(self, request):
        form = StartDiscussionForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()

            new_post_url = reverse('discussion', args=[post.id])
            return HttpResponseRedirect(new_post_url)
        else:
            return render(request, "submit.html", context={"form": form})

@login_required
@require_http_methods(['POST'])
def upvote_post(request, post_id):
    _vote_on_post(request, post_id, UPVOTE)
    return HttpResponse('OK')

@login_required
@require_http_methods(['POST'])
def downvote_post(request, post_id):
    _vote_on_post(request, post_id, DOWNVOTE)
    return HttpResponse('OK')

@login_required
@require_http_methods(['POST'])
def undo_vote_on_post(request, post_id):
    post_type = ContentType.objects.get_for_model(Post)
    Vote.objects.filter(content_type=post_type.id,
            object_id=post_id,\
            voter=request.user).delete()
    return HttpResponse('OK')

def _vote_on_post(request, post_id, type_of_vote):
    post = get_object_or_404(Post, pk=post_id)

    if _already_voted(request.user, post, type_of_vote):
        return

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
    
def _already_voted(user, post, type_of_vote):
    post_type = ContentType.objects.get_for_model(post)
    return Vote.objects.filter(content_type=post_type.id,
                object_id=post.id,\
                voter=user, type_of_vote=type_of_vote)\
            .exists()

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
