import os, re
from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from photos.models import Image

from activity_stream.models import *

class StoryTest(TestCase):
    def setUp(self):
        self.file_path = os.path.join(os.path.realpath(os.path.dirname(__file__)), "../../test_data")
        
    def test_batching(self):
        c = Client()
        c.login(username='admin', password='localhost')
        photo = Image.objects.create(title="1", title_slug="1")
        photo.image.save(os.path.basename('photo.jpg'), ContentFile(open(self.file_path+'/photo.jpg', "r").read()))
        photo.save()
        activityItem = create_activity_item("placed", User.objects.get(username="admin"), photo)
        self.assertTrue(activityItem)
        self.assertEquals(activityItem.is_batched, False)
        self.assertEquals(activityItem.subjects.count(), 1)

        activityItem2 = create_activity_item("placed", User.objects.get(username="admin"), photo)
        self.assertTrue(activityItem2)
        self.assertEquals(activityItem2.is_batched, True)
        self.assertEquals(activityItem2.subjects.count(), 2)

