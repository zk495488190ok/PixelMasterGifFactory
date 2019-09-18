# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from PIL import Image
import numpy as np
from learn.picaifactory.utils.sql.sqldb import db
# from learn.picaifactory.utils.picai.picaiutil import picutil
import os

from django.test import TestCase
# Create your tests here.

# db.recoredLoginInfo('openid_xxxx', '555555555555', '555555555555')

# db.recoredFuncUse('oatGa5YE9zO2MM9VCGmAyWxccJNc',0)

# picutil.styleTransform('wave.ckpt-done','test23.jpg')

# inpath = os.path.abspath('../static/picaifactory/img/' + 'oatGa5YE9zO2MM9VCGmAyWxccJNc2.jpg')
# picutil.compress_image(inpath,inpath)


db.getUsers()