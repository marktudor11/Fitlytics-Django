from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.conf import settings
import os

class ChatViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user("tester","tester@example.com","pass123")
        # Ensure env key present (dummy if not)
        os.environ.setdefault("GEMINI_API_KEY", settings.GEMINI_API_KEY or "dummy")

    def test_requires_login(self):
        r = self.client.post(reverse("assistant:chat"), {"q":"Test"})
        self.assertEqual(r.status_code, 302)

    def test_empty_question(self):
        self.client.login(username="tester", password="pass123")
        r = self.client.post(reverse("assistant:chat"), {"q":"   "})
        self.assertEqual(r.status_code, 400)

    def test_basic_post(self):
        self.client.login(username="tester", password="pass123")
        r = self.client.post(reverse("assistant:chat"), {"q":"Leg day ideas"})
        self.assertIn(r.status_code, (200, 500))
        self.assertIn("answer", r.json())