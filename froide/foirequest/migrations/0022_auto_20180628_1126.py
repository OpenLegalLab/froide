# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-06-28 09:26
from __future__ import unicode_literals

from django.db import migrations


def set_message_kind(apps, schema_editor):
    FoiMessage = apps.get_model("foirequest", "FoiMessage")
    FoiMessage.objects.filter(is_postal=True).update(kind="post")


class Migration(migrations.Migration):

    dependencies = [
        ("foirequest", "0021_foimessage_kind"),
    ]

    operations = [
        migrations.RunPython(set_message_kind),
    ]
