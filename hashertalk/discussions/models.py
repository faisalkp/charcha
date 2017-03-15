from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MinValueValidator, MaxValueValidator

UPVOTE = 1
DOWNVOTE = 2
FLAG = 3
UNFLAG = 4

class Vote(models.Model):
    class Meta:
        db_table = "votes"
        index_together = [
            ["content_type", "object_id"],
        ]
        
    # The following 3 fields represent the Comment or Post
    # on which a vote has been cast
    # See Generic Relations in Django's documentation
    content_type = models.ForeignKey(ContentType, on_delete=models.PROTECT)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    voter = models.ForeignKey(User, on_delete=models.PROTECT)
    type_of_vote = models.IntegerField(choices = (
            (UPVOTE, 'Upvote'),
            (DOWNVOTE, 'Downvote'),
            (FLAG, 'Flag'),
            (UNFLAG, 'Unflag'),
        ))
    submission_time = models.DateTimeField(auto_now_add=True)

class Votable(models.Model):
    class Meta:
        abstract = True

    votes = GenericRelation(Vote)

    # denormalization to save database queries
    # score = count(upvotes) - count(downvotes)
    # flags = count of votes of type "Flag"
    score = models.IntegerField(default=0)
    flags = models.IntegerField(default=0)
    
class Post(Votable):
    class Meta:
        db_table = "posts"
        index_together = [
            ["submission_time",],
        ]
    title = models.CharField(max_length=120)
    url = models.URLField(blank=True)
    text = models.TextField(blank=True, max_length=8192)
    author = models.ForeignKey(User, on_delete=models.PROTECT)
    submission_time = models.DateTimeField(auto_now_add=True)
    num_comments = models.IntegerField(default=0)

    def __str__(self):
        return self.title

class Comment(Votable):
    class Meta:
        db_table = "comments"
        index_together = [
            ["post", "wbs"],
        ]

    post = models.ForeignKey(Post, related_name="comments")
    parent_comment = models.ForeignKey('self', 
                null=True, blank=True,
                on_delete=models.PROTECT)
    text = models.TextField(max_length=8192)
    author = models.ForeignKey(User, on_delete=models.PROTECT)
    submission_time = models.DateTimeField(auto_now_add=True)
    
    # wbs helps us to track the comments as a tree
    # Format is 0000.0000.0000.0000.0000.0000
    # This means that:
    # 1. We only allow 9999 comments at each level
    # 2. We allow threaded comments upto 6 levels
    wbs = models.CharField(max_length=29)

    def __str__(self):
        return self.text

class Favourite(models.Model):
    class Meta:
        # Yes, I use Queen's english
        db_table = "favourites"

    # The following 3 fields represent the Comment or Post
    # which has been favourited
    # See Generic Relations in Django's documentation
    content_type = models.ForeignKey(ContentType, on_delete=models.PROTECT)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    favourited_on = models.DateTimeField(auto_now_add=True)
    deleted_on = models.DateTimeField(blank=True, null=True)
