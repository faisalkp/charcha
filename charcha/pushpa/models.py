from django.db import models
from charcha.discussions.models import User
from pywebpush import WebPusher
import json
from django.conf import settings

GCM_KEY="AAAAg6WtQoE:APA91bH4OzX-QkBbnie4WCMDWmEMf0dIxXRr_TdRB-FWB5GxHgRve6lfBpWuUkuLg-GIJCAPIhkD9Zh6-zFgVPaGQARhn4HayPDGhx35T8s1AaGZXEv0BJVqQBPvp6WZ4Z3VUcOw21Bf"
class Subscription(models.Model):
    class Meta:
        db_table = "user_push_notification_subscriptions"
        unique_together = [
            ["user", "endpoint"],
        ]
    
    # This is a one-to-many relationship because
    # a user can have multiple devices
    user = models.ForeignKey(User, 
        related_name="subscriptions", on_delete=models.PROTECT)
    
    browser = models.CharField(max_length=100)
    endpoint = models.URLField(max_length=350)
    auth = models.CharField(max_length=100)
    p256dh = models.CharField(max_length=100)

    def send_notification(self, title, options, ttl=86400):
        subscription = {
            "endpoint": self.endpoint,
            "keys": {
                "auth": self.auth,
                "p256dh": self.p256dh
            }
        }
        payload = {
            "title": title,
            "options": options or {}
        }
        WebPusher(subscription).\
            send(json.dumps(payload), {}, ttl, GCM_KEY)
