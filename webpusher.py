from pywebpush import WebPusher
import json

subscription = {
    "endpoint": "https://android.googleapis.com/gcm/send/d7NYbr3L_OE:APA91bEoBDTAKMTbgRKimkM8AR-VERt0bnaYD1XM8rIQAhy8bab_73naboNzcrPOjcQpwEntpPiZlJcLQN1xdflz9UxMO75IyqynszbX06FedaAPM1u9v-NyNFuiVpWT3j1iYJCRZAfp",
    "keys": {
        "auth": "6_vF1eMfEHCQGeRxuD-74w==",
        "p256dh": "BEyblDkQ20dmG0nbTdbSwkkbY_9KhbmzELac9_PfgnynQu-MxnCEtEGGDAOEyfvY3GBBR6mp49Fp_lSTyW6CARA="
    }
}

gcm_key = "AAAAg6WtQoE:APA91bH4OzX-QkBbnie4WCMDWmEMf0dIxXRr_TdRB-FWB5GxHgRve6lfBpWuUkuLg-GIJCAPIhkD9Zh6-zFgVPaGQARhn4HayPDGhx35T8s1AaGZXEv0BJVqQBPvp6WZ4Z3VUcOw21Bf"

payload = {
    "title": "Himanshu replied to your comment",
    "options": {
      "body": "Can we build this differently?...",
      "icon": "/apple-icon-120x120.png",
      "badge": "/android-icon-96x96.png",
      "actions": [
        {
          "action": "http://localhost:8000/discuss/5/",
          "title": "View Discussion",
          "icon": "/open-new-window.png"
        }
      ]
    }
}

WebPusher(subscription).send(json.dumps(payload), {}, 10000, gcm_key)



# New Post
# Reply
# 