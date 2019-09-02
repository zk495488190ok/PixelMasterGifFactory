# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.conf import settings
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse, JsonResponse
import json
import os
from pixel.pixelutils import pixel
from PIL import Image
import io
import requests

# Create your views here.
# coding:utf-8

def index(request):
    return response(200,"欢迎访问,可别干坏事哦!^_^","")


# # # # # # # # # # # # 从腾讯接口获取OpenID # # # # # # # # # # # #
def getOpenID(request):
    code = request.GET['code']
    wxurl = "https://api.weixin.qq.com/sns/jscode2session?appid="+ settings.WX_APP_ID +"&secret="+ settings.WX_SECRET_KEY +"&js_code=" + code + "&grant_type=authorization_code"
    resContent = requests.get(wxurl)
    if(resContent.status_code != 200):
        return response(201,"","api.weixin.qq.com 获取openID 出现异常")
    resDic = eval(resContent.text)
    return response(200, resDic, "")


# # # # # # # # # # # # 创建GIF # # # # # # # # # # # #
@require_http_methods(["POST"])
def createGIF(request):
    dataLen = 1024
    speedStr = request.POST['speed']
    dataArrStr = request.POST['dataArr']
    openid = request.POST["openid"]  ###可随便传没有本地数据库 无法做验证,暂做图片唯一id

    #--------- 验证 ---------
    if len(openid) == 0:
        return response(201,"","openid 不能为空哦")

    if len(speedStr) == 0 | len(dataArrStr) == 0 | (len(dataArrStr) % 1024 != 0):
        return response(201,"","参数数据不正确")

    speed = int(speedStr)
    dataArr = dataArrStr.split(',')
    if(len(dataArr) == 0):
        return response(201,"","不支持单张生成哦")
    #--------- 生成 ---------
    createDataArr = []
    count = int(len(dataArr) / dataLen)
    for i in range(0,count):
        data = dataArr[i * dataLen:(i + 1) * dataLen]
        createDataArr.append(data)

    httpPath = "static/images/" + openid + ".gif"
    filePath = "./" + httpPath
    status = pixel.createGIFWithRGBADataArr(createDataArr,15,filePath,speed /1000)
    if status == -1:
        return response(201,"","zoom参数不能小于1的哦")
    elif status == 1:
        return  response(201,"","不支持单帧图片哦")
    else:
        retGifUrl = 'http://' + request.get_host() + "/" + httpPath
        print(retGifUrl)
        return response(200, retGifUrl, "")



# # # # # # # # # # # # 转化上传的GIF 图片 # # # # # # # # # # # #
# @require_http_methods(["POST"])
def upload(request):
    file = request.FILES.get("file",None)
    openid = request.POST["openid"]
    ext = pGetFileExtension(file.name)

    if pIsAllowedImageType(ext) == False:
        return response(201,"","服务器只处理gif动画哦！")
    if pIsAllowedFileSize(file.size) == False:
        return response(201,"","文件过大,不支持处理")

    httpPath = "static/images/" + openid + "." + file.name.split('.')[-1];
    filePath = "./" + httpPath
    with open(filePath,"wb+") as f:
        # 分块写入
        for chunk in file.chunks():
            f.write(chunk)
    imgPixelData = pixel.gifConvertToRBGADataArrWithPath(filePath,16)
    return response(200,imgPixelData,"")


# -----------------------------

def response(status,successData,errorMsgStr):
    data = {"status":status,"data":successData,"errorMsg":errorMsgStr}
    res = JsonResponse(data=data,status=status)
    return res

# 文件类型过滤 我们只允许上传常用的图片文件
def pIsAllowedImageType(ext):
    if ext in [".gif",".GIF"]:
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