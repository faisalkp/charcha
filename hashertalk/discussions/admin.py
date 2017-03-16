from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from .models import Post, Comment, Vote, Favourite

class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'url')
    
class CommentAdmin(admin.ModelAdmin):
    list_display = ('submission_time', 'post', 'wbs', 'author', 'text')

class VoteAdmin(admin.ModelAdmin):
    list_display = ('content_object', 'voter', 'type_of_vote', 'submission_time')

class FavouriteAdmin(admin.ModelAdmin):
    pass

admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Vote, VoteAdmin)
admin.site.register(Favourite, FavouriteAdmin)
