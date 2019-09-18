# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.conf import settings
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse, JsonResponse
import requests

from learn.picaifactory.utils.sql.sqldb import db



def index(request):
    context = {}
    context["users"] = db.getUsers()
    index_page = render(request,"bgmgr/users/users.html",context)
    return index_page