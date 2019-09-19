# -*- coding: utf-8 -*-

import cv2
import time
import os
import glob
import ssl

import threading
from PIL import Image

import tensorflow as tf
from learn.picaifactory.utils.picai.preprocessing import preprocessing_factory
import learn.picaifactory.utils.picai.reader as reader
import learn.picaifactory.utils.picai.model as model


import requests
import simplejson
import json
import base64

apikey = "rSiOWwOp_fgdXqArclpcCJf52D2LETbh"
apiSecret = "6BBgYV9viRzt9dZne_kVRCqjBa4T9veT"

class picaiutil:
    # _instance_lock = threading.Lock()
    # _models = {}

    def __init__(self):
        pass

    # def __new__(cls, *args, **kwargs):
    #     if not hasattr(picaiutil, "_instance"):
    #         with picaiutil._instance_lock:
    #             if not hasattr(picaiutil, "_instance"):
    #                 picaiutil._instance = object.__new__(cls)
    #     return picaiutil._instance

    # 人脸识别
    def find_face(self,imgpath):
        print("识别人脸")
        http_url = 'https://api-cn.faceplusplus.com/facepp/v3/detect'
        data = {"api_key": apikey,
                "api_secret": apiSecret, "image_url": imgpath, "return_landmark": 1}
        files = {"image_file": open(imgpath, "rb")}
        response = requests.post(http_url, data=data, files=files)
        req_con = response.content.decode('utf-8')
        req_dict = json.JSONDecoder().decode(req_con)
        this_json = simplejson.dumps(req_dict)
        this_json2 = simplejson.loads(this_json)
        faces = this_json2['faces']
        if len(faces) <= 0:
            return -1
        list0 = faces[0]
        rectangle = list0['face_rectangle']
        return rectangle

    # AI换脸
    def merge_face(self,image_url_1, image_url_2, image_url, number):
        ff1 = self.find_face(image_url_1)
        ff2 = self.find_face(image_url_2)
        if ff1 == -1 or ff2 == -1:
            return -1
        rectangle1 = str(str(ff1['top']) + "," + str(ff1['left']) + "," + str(ff1['width']) + "," + str(ff1['height']))
        rectangle2 = str(ff2['top']) + "," + str(ff2['left']) + "," + str(ff2['width']) + "," + str(ff2['height'])
        url_add = "https://api-cn.faceplusplus.com/imagepp/v1/mergeface"
        f1 = open(image_url_1, 'rb')
        f1_64 = base64.b64encode(f1.read())
        f1.close()
        f2 = open(image_url_2, 'rb')
        f2_64 = base64.b64encode(f2.read())
        f2.close()
        data = {"api_key": apikey, "api_secret": apiSecret,
                "template_base64": f1_64, "template_rectangle": rectangle1,
                "merge_base64": f2_64, "merge_rectangle": rectangle2, "merge_rate": number}

        response = requests.post(url_add, data=data)
        req_con = response.content.decode('utf-8')
        req_dict = json.JSONDecoder().decode(req_con)
        result = req_dict['result']
        imgdata = base64.b64decode(result)
        file = open(image_url, 'wb')
        file.write(imgdata)
        print('换脸完成')


    # 风格转换
    def styleTransform(self,modelName, imgName):
        modelPath = os.path.abspath('static/picaifactory/models/'+modelName)
        imgPath = os.path.abspath('static/picaifactory/img/' + imgName)
        resultPath = os.path.abspath('static/picaifactory/result/')


        if os.path.exists(modelPath) is False:
            return "训练模型不存在!"
        if os.path.exists(imgPath) is False:
            return "您的操作图片还没有上传!"

        # Get image's height and width.
        height = 0
        width = 0
        print('正在转换...')
        with open(imgPath, 'rb') as img:
            with tf.compat.v1.Session().as_default() as sess:
                if imgPath.lower().endswith('png'):
                    image = sess.run(tf.image.decode_png(img.read()))
                else:
                    image = sess.run(tf.image.decode_jpeg(img.read()))

                height = image.shape[0]
                width = image.shape[1]
                if width * height > 300000 :
                    scale = 600 / max(width,height);
                    width = int(width * scale);
                    height = int(height * scale);

        with tf.Graph().as_default():
            with tf.compat.v1.Session().as_default() as sess:
                # Read image data.
                image_preprocessing_fn, _ = preprocessing_factory.get_preprocessing(
                    'vgg_16',
                    is_training=False)
                image = reader.get_image(imgPath, height, width, image_preprocessing_fn)

                # Add batch dimension
                image = tf.expand_dims(image, 0)

                generated = model.net(image, training=False)
                generated = tf.cast(generated, tf.uint8)

                # Remove batch dimension
                generated = tf.squeeze(generated, [0])

                # Restore model variables.
                saver = tf.compat.v1.train.Saver(tf.compat.v1.global_variables(),
                                                 write_version=tf.compat.v1.train.SaverDef.V1)
                sess.run([tf.compat.v1.global_variables_initializer(), tf.compat.v1.local_variables_initializer()])
                # Use absolute path
                saver.restore(sess, modelPath)

                # Make sure 'generated' directory exists.
                generated_dir = resultPath + '/'
                generated_file = generated_dir + imgName
                if os.path.exists(generated_dir) is False:
                    os.makedirs(generated_dir)

                # Generate and write image data to file.
                with open(generated_file, 'wb') as img:
                    start_time = time.time()
                    img.write(sess.run(tf.image.encode_jpeg(generated)))
                    end_time = time.time()
                    print('转换完成...');
                    print('用时: %fs' % (end_time - start_time))
                    print('生成路径:%s.' % generated_file)
                    return ''

    def compress_image(self,filepath,outfilepath,maxWH):
        ysimg = Image.open(filepath)
        w,h = ysimg.size
        if min(w,h) > maxWH:
            scale = maxWH / min(w, h);
            w = int(w * scale);
            h = int(h * scale);

        ysimg =ysimg.resize((w,h),Image.ANTIALIAS)
        ysimg = ysimg.convert("RGB")
        ysimg.save(outfilepath)

picutil = picaiutil()