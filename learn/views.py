# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

# Create your views here.
# coding:utf-8
from django.http import HttpResponse


def index(request):
    return HttpResponse(u"{\"speed\":300,\"data\":[\"1\",\"2\"]}")