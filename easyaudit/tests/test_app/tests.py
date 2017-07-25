# -*- coding: utf-8 -*-
import json
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from test_app.models import TestModel, TestForeignKey, TestM2M
from easyaudit.models import CRUDEvent


TEST_USER_EMAIL = 'joe@example.com'
TEST_USER_PASSWORD = 'password'

class TestAuditModels(TestCase):
    
    def test_create_model(self):
        obj = TestModel.objects.create()
        self.assertEqual(obj.id, 1)
        crud_event_qs = CRUDEvent.objects.filter(object_id=obj.id, content_type=ContentType.objects.get_for_model(obj))
        self.assertEqual(1, crud_event_qs.count())
        crud_event = crud_event_qs[0]
        data = json.loads(crud_event.object_json_repr)[0]
        self.assertEqual(data['fields']['name'], obj.name)


class TestMiddleware(TestCase):
    def _setup_user(self, email, password):
        user = User(username=email)
        user.set_password(password)
        user.save()
        return user

    def _log_in_user(self, email, password):
        login = self.client.login(username=email, password=password)
        self.assertTrue(login)

    def test_middleware_logged_in(self):
        user = self._setup_user(TEST_USER_EMAIL, TEST_USER_PASSWORD)
        self._log_in_user(TEST_USER_EMAIL, TEST_USER_PASSWORD)
        create_obj_url = reverse("test_app:create-obj")
        self.client.post(create_obj_url)
        self.assertEqual(TestModel.objects.count(), 1)
        obj = TestModel.objects.all()[0]
        crud_event = CRUDEvent.objects.filter(object_id=obj.id, content_type=ContentType.objects.get_for_model(obj))[0]
        self.assertEqual(crud_event.user, user)
