from __future__ import with_statement
import re

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.conf import settings
from django.core import mail
from django.utils import translation
from django.contrib.auth.models import User

from foirequest.models import FoiRequest
from foirequestfollower.models import FoiRequestFollower


class FoiRequestFollowerTest(TestCase):
    fixtures = ['auth_profile.json', 'publicbody.json', 'foirequest.json']

    def setup(self):
        translation.activate(settings.LANGUAGE_CODE)

    def test_following(self):
        req = FoiRequest.objects.all()[0]
        user = User.objects.get(username='sw')
        self.client.login(username='sw', password='froide')
        response = self.client.post(reverse('foirequestfollower-follow',
                kwargs={"slug": req.slug}))
        # Can't follow my own requests
        self.assertEqual(response.status_code, 400)
        try:
            FoiRequestFollower.objects.get(request=req, user=user)
        except FoiRequestFollower.DoesNotExist:
            pass
        else:
            self.assertTrue(False)
        self.client.logout()
        user = User.objects.get(username='dummy')
        self.client.login(username='dummy', password='froide')
        response = self.client.post(reverse('foirequestfollower-follow',
                kwargs={"slug": req.slug}))
        self.assertEqual(response.status_code, 302)
        follower = FoiRequestFollower.objects.get(request=req, user=user)
        self.assertEqual(len(mail.outbox), 0)
        req.add_postal_reply.send(sender=req)
        self.assertEqual(len(mail.outbox), 1)
        mes = mail.outbox[0]
        match = re.search('/%d/(\w+)/' % follower.pk, mes.body)
        check = match.group(1)
        response = self.client.get(
            reverse('foirequestfollower-confirm_unfollow',
                kwargs={'follow_id': follower.id,
                        'check': "a" * 32}))
        self.assertEqual(response.status_code, 302)
        follower = FoiRequestFollower.objects.get(request=req, user=user)
        response = self.client.get(
            reverse('foirequestfollower-confirm_unfollow',
                kwargs={'follow_id': follower.id,
                        'check': check}))
        self.assertEqual(response.status_code, 302)
        try:
            FoiRequestFollower.objects.get(request=req, user=user)
        except FoiRequestFollower.DoesNotExist:
            pass
        else:
            self.assertTrue(False)
