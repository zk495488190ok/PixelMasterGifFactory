"""untitled8 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from learn import views as learn_views  # new
from learn.picaifactory import action as picaiafactory_actions  # new
from learn.bgmgr.users import users #new

urlpatterns = [

    # 像素工厂
    url(r'^$', learn_views.index),
    url(r'^upload/', learn_views.upload),
    url(r'^createGIF/', learn_views.createGIF),
    url(r'^getOpenID/', learn_views.getOpenID),

    # 图片工厂
    url(r'^picai/styletransform/', picaiafactory_actions.styletransform),
    url(r'^picai/getOpenID/', picaiafactory_actions.getOpenID),
    url(r'^picai/upload/', picaiafactory_actions.upload),
    url(r'^picai/recoreUinfo/', picaiafactory_actions.recoreUinfo),
    url(r'^picai/recoredFuncUse/', picaiafactory_actions.recoredFuncUse),
    url(r'^picai/mergeFace/', picaiafactory_actions.mergeFace),

    #后台管理
    url(r'^admin/', admin.site.urls),
    url(r'^bgmgr/users/', users.index),
]


