# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.conf import settings
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse, JsonResponse

import json
import os
import io
import requests

from learn.picaifactory.utils.picai.picaiutil import picutil
from learn.picaifactory.utils.sql.sqldb import db

# # # # # # # # # # # # 从腾讯接口获取OpenID # # # # # # # # # # # #
def getOpenID(request):
    code = request.GET['code']
    wxurl = "https://api.weixin.qq.com/sns/jscode2session?appid="+ settings.PIC_FACTORY_WX_APP_ID +"&secret="+ settings.PIC_FACTORY_WX_SECRET_KEY +"&js_code=" + code + "&grant_type=authorization_code"
    resContent = requests.get(wxurl)
    if(resContent.status_code != 200):
        return response(201,"","api.weixin.qq.com 获取openID 出现异常")
    resDic = eval(resContent.text)
    return response(200, resDic, "")


# # # # # # # # # # # # 记录授权用户信息 # # # # # # # # # # # #
def recoredFuncUse(request):
    try:
        openid = request.POST["openid"]
        funcID = request.POST["funcID"]
        if len(openid) == 0 or len(funcID) == 0:
            return response(201, "", "别瞎几把搞!")
        db.recoredFuncUse(openid,funcID)
        return response(200, "sucess", "")
    except Exception as err:
        return response(201, "", "别瞎几把搞!")

# # # # # # # # # # # # 记录授权用户信息 # # # # # # # # # # # #
# @require_http_methods(["POST"])
def recoreUinfo(request):
    try:
        openid = request.POST["openid"]
        nickname = request.POST["nickname"]
        icon = request.POST["icon"]
        if len(openid) == 0 or len(nickname) == 0 or len(icon) == 0:
            return response(201, "", "别瞎几把搞!")
        try:
            db.recoredLoginInfo(openid, nickname, icon)
            return response(200, "sucess", "")
        except Exception as err:
            return response(201, "", "数据操作异常")
    except Exception as err:
        return response(201, "", "别瞎几把搞!")

# # # # # # # # # # # # 转化上传的GIF 图片 # # # # # # # # # # # #
# @require_http_methods(["POST"])
def upload(request):
    file = request.FILES.get("file",None)
    openid = request.POST["openid"]
    ext = pGetFileExtension(file.name)

    if len(openid) == 0:
        return response(201, "", "别瞎几把搞!")

    if pIsAllowedImageType(ext) == False:
        return response(201,"","只限处理jpg jpeg png哦！")
    if pIsAllowedFileSize(file.size) == False:
        return response(201,"","文件过大,不支持处理")

    # httpPath = "static/picaifactory/" + openid + "." + file.name.split('.')[-1];
    httpPath = "static/picaifactory/img/" + openid + ".jpg";
    filePath = "./" + httpPath

    if os.path.exists(filePath) is False:
        os.makedirs(filePath)

    with open(filePath,"wb+") as f:
        # 分块写入
        for chunk in file.chunks():
            f.write(chunk)
    return response(200,httpPath,"")




# # # # # # # # # # # #  风格学习  # # # # # # # # # # # #
def styletransform(request):
    modeName = request.GET["mode_name"]
    openid = request.GET["openid"]
    if len(openid) == 0 or len(modeName) == 0:
        return response(201, "", "别瞎几把搞!")

    imgName = openid + ".jpg";
    resMsg = picutil.styleTransform(modeName,imgName)
    if len(resMsg) > 0:
        return response(201, "", resMsg)
    else:
        returl = "static/picaifactory/result/" + openid + ".jpg";
        return response(200, returl, "")



# -----------------------------

def response(status,successData,errorMsgStr):
    data = {"status":status,"data":successData,"errorMsg":errorMsgStr}
    res = JsonResponse(data=data,status=status)
    return res

# 文件类型过滤 我们只允许上传常用的图片文件
def pIsAllowedImageType(ext):
    if ext in [".jpg",".JPG",".png",".PNG",".JPEG",".jpeg"]:
        return True
    return False

# 文件大小限制
def pIsAllowedFileSize(size):
    limit = 5 * 1024 * 1024
    if size < limit:
        return True
    return False

# 检测文件类型
def pGetFileExtension(file):
    return os.path.splitext(file)[1]