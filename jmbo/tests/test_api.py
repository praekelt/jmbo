import os
import unittest
import json

from django.core.urlresolvers import reverse
from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.test.client import Client

from rest_framework.test import APIClient

from jmbo.models import ModelBase, Image, ModelBaseImage
from jmbo.tests.models import TestModel


RES_DIR = os.path.join(os.path.dirname(__file__), "res")
IMAGE_PATH = os.path.join(RES_DIR, "image.jpg")


class APITestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = APIClient()

        # Editor
        cls.editor = get_user_model().objects.create(
            username="editor-api",
            email="editor-api@test.com",
            is_superuser=True,
            is_staff=True
        )
        cls.editor.set_password("password")
        cls.editor.save()

        # Prep
        cls.client.logout()
        Site.objects.all().delete()
        Site.objects.create(id=1, domain="site.example.com")
        ModelBase.objects.all().delete()

        # Objects for this test
        cls.obj1 = TestModel(title="title1")
        cls.obj1.save()
        cls.obj2 = TestModel(title="title2", state="published")
        cls.obj2.save()
        cls.obj2.sites = Site.objects.all()
        cls.obj2.save()

        cls.image = Image.objects.create(title=IMAGE_PATH)
        cls.image.image.save(
            os.path.basename(IMAGE_PATH),
            ContentFile(open(IMAGE_PATH, "rb").read())
        )
        cls.mbi1 = ModelBaseImage.objects.create(
            modelbase=cls.obj1, image=cls.image
        )
        cls.mbi2 = ModelBaseImage.objects.create(
            modelbase=cls.obj2, image=cls.image
        )

    def setUp(self):
        self.client.logout()

    def login(self):
        self.client.login(username="editor-api", password="password")

    def test_modelbase_list(self):
        response = self.client.get("/api/v1/jmbo-modelbase/")
        self.assertEqual(response.status_code, 403)
        self.login()
        response = self.client.get("/api/v1/jmbo-modelbase/")
        as_json = json.loads(response.content)
        self.assertEqual(response.status_code, 200)

    def test_permitted_modelbase_list(self):
        response = self.client.get("/api/v1/jmbo-permitted-modelbase/")
        as_json = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(as_json), 1)

    def test_testmodel_list(self):
        response = self.client.get("/api/v1/tests-testmodel/")
        self.assertEqual(response.status_code, 403)
        self.login()
        response = self.client.get("/api/v1/tests-testmodel/")
        as_json = json.loads(response.content)
        self.assertEqual(response.status_code, 200)

    def test_permitted_testmodel_list(self):
        response = self.client.get("/api/v1/tests-permitted-testmodel/")
        as_json = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(as_json), 1)

    def test_testmodel_create(self):
        """Light test since DRF and DRFE already test similar paths"""
        self.login()
        new_pk = TestModel.objects.all().last().id + 1
        data = {
            "title": "title",
            "slug": "title",
            "content": "content"
        }
        response = self.client.post("/api/v1/tests-testmodel/", data)
        as_json = json.loads(response.content)
        self.assertEqual(as_json["content"], "content")
        self.assertTrue(TestModel.objects.filter(pk=new_pk).exists())

    def test_modelbase_publish(self):
        response = self.client.post("/api/v1/jmbo-modelbase/%s/publish/" % self.obj1.pk)
        self.assertEqual(response.status_code, 403)
        self.login()
        response = self.client.post("/api/v1/jmbo-modelbase/%s/publish/" % self.obj1.pk)
        as_json = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(as_json["status"], "success")
        self.assertEqual(ModelBase.objects.get(pk=self.obj1.pk).state, "published")

    def test_modelbase_unpublish(self):
        response = self.client.post("/api/v1/jmbo-modelbase/%s/unpublish/" % self.obj1.pk)
        self.assertEqual(response.status_code, 403)
        self.login()
        response = self.client.post("/api/v1/jmbo-modelbase/%s/unpublish/" % self.obj1.pk)
        as_json = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(as_json["status"], "success")
        self.assertEqual(ModelBase.objects.get(pk=self.obj1.pk).state, "unpublished")

    def test_modelbase_images(self):
        response = self.client.get("/api/v1/jmbo-modelbase/%s/images/" % self.obj1.pk)
        self.assertEqual(response.status_code, 403)
        self.login()
        response = self.client.get("/api/v1/jmbo-modelbase/%s/images/" % self.obj1.pk)
        as_json = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(as_json["status"], "success")
        self.assertEqual(
            as_json["images"],
            [u"http://testserver/api/v1/jmbo-image/%s/" % self.image.pk]
        )

    def test_permitted_modelbase_images(self):
        response = self.client.get("/api/v1/jmbo-permitted-modelbase/%s/images/" % self.obj2.pk)
        as_json = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(as_json["status"], "success")
        self.assertEqual(
            as_json["images"],
            [u"http://testserver/api/v1/jmbo-image/%s/" % self.image.pk]
        )

    def test_create_image(self):
        new_pk = Image.objects.all().last().id + 1
        fp = open(IMAGE_PATH, "rb")
        data = {
            "title": "title",
            "image": fp
        }
        response = self.client.post(
            "/api/v1/jmbo-image/",
            data,
            format="multipart"
        )
        self.assertEqual(response.status_code, 403)
        self.login()
        fp.seek(0)
        response = self.client.post(
            "/api/v1/jmbo-image/",
            data,
            format="multipart"
        )
        self.assertEqual(response.status_code, 201)
        as_json = json.loads(response.content)
        self.assertTrue(Image.objects.filter(pk=new_pk).exists())

    def test_create_modelbaseimage(self):
        new_pk = ModelBaseImage.objects.all().last().id + 1
        data = {
            "modelbase": "http://testserver/api/v1/jmbo-modelbase/%s/" % self.obj1.pk,
            "image": "http://testserver/api/v1/jmbo-image/%s/" % self.image.pk,
        }
        response = self.client.post(
            "/api/v1/jmbo-modelbaseimage/",
            data,
        )
        self.assertEqual(response.status_code, 403)
        self.login()
        response = self.client.post(
            "/api/v1/jmbo-modelbaseimage/",
            data,
        )
        self.assertEqual(response.status_code, 201)
        as_json = json.loads(response.content)
        self.assertTrue(ModelBaseImage.objects.filter(pk=new_pk).exists())
        # Delete it because it pollutes other tests
        ModelBaseImage.objects.filter(pk=new_pk).delete()
