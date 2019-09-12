# -*- coding: utf-8 -*-

import cv2
import time
import os
import glob

import threading
from PIL import Image

import tensorflow as tf
from learn.picaifactory.utils.picai.preprocessing import preprocessing_factory
import learn.picaifactory.utils.picai.reader as reader
import learn.picaifactory.utils.picai.model as model

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



    def initModels(self):
        models = {}
        print('初始化训练模型')
        start = time.time()
        for url in glob.glob('./static/picaifactory/models/*.t7'):
            net = cv2.dnn.readNetFromTorch(url)
            models[url] = net
        end = time.time()
        print('初始化完成')
        print("用时：{:.2f}秒".format(end - start))
        return models

    def styleTransform(self,modelName, imgName):
        modelPath = os.path.abspath('static/picaifactory/models/'+modelName)
        imgPath = os.path.abspath('static/picaifactory/img/' + imgName)
        resultPath = os.path.abspath('static/picaifactory/result/')

        #转换前压缩图片
        self.compress_image(imgPath,imgPath)

        if os.path.exists(modelPath) is False:
            return "训练模型不存在!"
        if os.path.exists(imgPath) is False:
            return "您的操作图片还没有上传!"

        # Get image's height and width.
        height = 0
        width = 0
        print('正在转换...');
        with open(imgPath, 'rb') as img:
            with tf.compat.v1.Session().as_default() as sess:
                if imgPath.lower().endswith('png'):
                    image = sess.run(tf.image.decode_png(img.read()))
                else:
                    image = sess.run(tf.image.decode_jpeg(img.read()))
                height = image.shape[0]
                width = image.shape[1]
                if min(width,height) > 500 :
                    scale = 500 / min(width,height);
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

    def compress_image(self,filepath,outfilepath):
        ysimg = Image.open(filepath)
        w,h = ysimg.size
        if min(w,h) > 500:
            scale = 500 / min(w, h);
            w = int(w * scale);
            h = int(h * scale);

        ysimg =ysimg.resize((w,h),Image.ANTIALIAS)
        ysimg.save(outfilepath)

picutil = picaiutil()