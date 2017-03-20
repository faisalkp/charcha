from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import F

UPVOTE = 1
DOWNVOTE = 2
FLAG = 3

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
    
    def upvote(self, user):
        self._vote(user, UPVOTE)
    
    def downvote(self, user):
        self._vote(user, DOWNVOTE)
    
    def flag(self, user):
        self._vote(user, FLAG)

    def unflag(self, user):
        raise Exception("not yet implemented")

    def undo_vote(self, user):
        content_type = ContentType.objects.get_for_model(self)
        votes = Vote.objects.filter(content_type=content_type.id,
            object_id=self.id, type_of_vote__in=(UPVOTE, DOWNVOTE),
            voter=user)
        
        upvotes = 0
        downvotes = 0
        for v in votes:
            if v.type_of_vote == UPVOTE:
                upvotes = upvotes + 1
            elif v.type_of_vote == DOWNVOTE:
                downvotes = downvotes + 1
            else:
                raise Exception("Invalid state, logic bug in undo_vote")
            v.delete()

        self.score = F('score') - upvotes + downvotes
        self.save()
    
    def _vote(self, user, type_of_vote):
        content_type = ContentType.objects.get_for_model(self)
        if self._already_voted(user, content_type, type_of_vote):
            return

        # First, save the vote
        vote = Vote(content_object=self, voter=user, 
            type_of_vote=type_of_vote)
        vote.save()

        # Next, update our denormalized columns - flags and score
        if type_of_vote == FLAG:
            self.flags = F('flags') + 1
        elif type_of_vote == UPVOTE:
            self.score = F('score') + 1
        elif type_of_vote == DOWNVOTE:
            self.score = F('score') - 1
        else:
            raise Exception("Invalid type of vote " + type_of_vote)
        self.save()

    def _already_voted(self, user, content_type, type_of_vote):
        return Vote.objects.filter(content_type=content_type.id,
                    object_id=self.id,\
                    voter=user, type_of_vote=type_of_vote)\
                .exists()

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

# class CommentsManager(models.Manager):

#     def best_ones_first(self, post_id, user_id):
#         comment_type = ContentType.objects.get_for_model(Comment)
        
#         from django.db import connection
#         with connection.cursor() as cursor:
#             cursor.execute("""
#                 SELECT c.id, c.text, u.username, c.submission_time,
#                 c.wbs, 
#             """)
#         pass

#     pass

class Comment(Votable):
    class Meta:
        db_table = "comments"
        unique_together = [
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
    # Format is .0000.0000.0000.0000.0000.0000
    # This means that:
    # 1. We only allow 9999 comments at each level
    # 2. We allow threaded comments upto 6 levels
    wbs = models.CharField(max_length=30)

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
