from django.test import TestCase
from django.contrib.auth.models import AnonymousUser, User
from .models import Post, Vote, Comment

class DiscussionTests(TestCase):
    def setUp(self):
        self._create_users()
        
    def _create_users(self):
        self.ramesh = User.objects.create_user(
            username="ramesh", password="top_secret")
        self.amit = User.objects.create_user(
            username="amit", password="top_secret")
        self.swetha = User.objects.create_user(
            username="swetha", password="top_secret")
        self.anamika = AnonymousUser()

    def new_discussion(self, user, title):
        post = Post(title=title,
            text="Does not matter",
            author=user)
        post.save()
        return post
        
    def test_voting_on_home_page(self):
        # Ramesh starts a discussion
        post = self.new_discussion(self.ramesh, "Ramesh's Biography")

        # Then Anamika views home page
        posts = Post.objects.recent_posts_with_my_votes()
        self.assertEquals(len(posts), 1)
        post = posts.first()
        self.assertEquals(post.score, 0)

        # Ramesh and Amit upvote the post
        post.upvote(self.ramesh)
        post.upvote(self.amit)

        # Home page as seen by Amit
        post = Post.objects.recent_posts_with_my_votes(self.amit).first()
        self.assertTrue('upvote' in post.my_votes)
        self.assertTrue('downvote' not in post.my_votes)
        self.assertEquals(post.score, 2)

        # Swetha downvotes
        post.downvote(self.swetha)

        # Home page as seen by Swetha
        post = Post.objects.recent_posts_with_my_votes(self.swetha).first()
        self.assertEquals(post.score, 1)
        self.assertTrue('upvote' not in post.my_votes)
        self.assertTrue('downvote' in post.my_votes)

        # Amit undo's his vote
        post.undo_vote(self.amit)

        # Home page as seen by Amit
        post = Post.objects.recent_posts_with_my_votes(self.amit).first()
        self.assertEquals(post.score, 0)
        self.assertTrue('upvote' not in post.my_votes)
        self.assertTrue('downvote' not in post.my_votes)        


    def test_comments_ordering(self):
        _c1 = "See my Biography!"
        _c2 = "Dude, this is terrible!"
        _c3 = "Why write your biography when you haven't achieved a thing!"
        _c4 = "Seriously, that's all you have to say?"

        post = self.new_discussion(self.ramesh, "Ramesh's Biography")
        
        rameshs_comment = post.add_comment(_c1, self.ramesh)
        amits_comment = rameshs_comment.reply(_c2, self.amit)
        swethas_comment = rameshs_comment.reply(_c3, self.swetha)
        rameshs_response = amits_comment.reply(_c4, self.ramesh)

        comments = [c.text for c in 
                    Comment.objects.best_ones_first(post.id, self.ramesh.id)]

        self.assertEquals(comments, [_c1, _c2, _c4, _c3])

    