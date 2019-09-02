#coding:utf-8

from PIL import Image
import imageio

class pixelutils:
    def analyseImage(self,path):
        '''
        Pre-process pass over the image to determine the mode (full or additive).
        Necessary as assessing single frames isn't reliable. Need to know the mode
        before processing all frames.
        '''
        im = Image.open(path)
        results = {
            'size': im.size,
            'mode': 'full',
        }
        try:
            while True:
                if im.tile:
                    tile = im.tile[0]
                    update_region = tile[1]
                    update_region_dimensions = update_region[2:]
                    if update_region_dimensions != im.size:
                        results['mode'] = 'partial'
                        break
                im.seek(im.tell() + 1)
        except EOFError:
            pass
        return results

    def processImage(self,path):
        retArr = []
        '''
        Iterate the GIF, extracting each frame.
        '''
        mode = self.analyseImage(path)['mode']

        im = Image.open(path)

        i = 0
        p = im.getpalette()
        last_frame = im.convert('RGBA')

        try:
            while True:

                '''
                If the GIF uses local colour tables, each frame will have its own palette.
                If not, we need to apply the global palette to the new frame.
                '''
                if not im.getpalette():
                    im.putpalette(p)

                new_frame = Image.new('RGBA', im.size)

                '''
                Is this file a "partial"-mode GIF where frames update a region of a different size to the entire image?
                If so, we need to construct the new frame by pasting it on top of the preceding frames.
                '''
                if mode == 'partial':
                    new_frame.paste(last_frame)

                new_frame.paste(im, (0, 0), im.convert('RGBA'))
                retArr.append(new_frame)
                i += 1
                last_frame = new_frame
                im.seek(im.tell() + 1)
        except EOFError:
            return retArr

    """中心裁剪正方形图片，防止数据转换出现异常崩溃"""

    def cropCenterRECImg(self,im):

        w, h = im.size
        cropSize = 0
        cropOffsetPosX = 0
        cropOffsetPosY = 0

        if w != h:
            cropSize = min(w, h)
            cropOffsetPos = (max(w, h) - cropSize) / 2
            print(cropOffsetPos)

            if w > h:
                cropOffsetPosX = cropOffsetPos
            else:
                cropOffsetPosY = cropOffsetPos
        else:
            return im

        try:
            im = im.crop((cropOffsetPosX, cropOffsetPosY, cropSize, cropOffsetPosY + cropSize))
            return im
        except EOFError:
            return None

    """图片转换指定矩阵大小的图片颜色数据"""

    def imgConvertMatrix(self,im, matrixSize):
        dataArr = []
        w, h = im.size
        if matrixSize > w | matrixSize > h | matrixSize == w | matrixSize == h:
            return dataArr
        offset = int(w / matrixSize)
        for y in range(0, matrixSize):
            for x in range(0, matrixSize):
                centerX = int((x * offset) + (offset / 2))
                centerY = int((y * offset) + (offset / 2))
                pixel = im.getpixel((centerX, centerY))
                dataArr.append(pixel[0])
                dataArr.append(pixel[1])
                dataArr.append(pixel[2])
                dataArr.append(pixel[3])

        return dataArr

    """GIF 图像转换对应矩阵大小的RGBA 颜色数据数组"""

    def gifConvertToRBGADataArrWithPath(self,path, matrixSize):
        retDataArr = []
        imgArr = self.processImage(path)
        for item in imgArr:
            img = self.cropCenterRECImg(item)
            pixelDataArr = self.imgConvertMatrix(img, matrixSize)
            retDataArr.append(pixelDataArr)

        return retDataArr

    """根据颜色数据 倍放生成 GIF"""

    def createGIFWithRGBADataArr(self,dataArr, zoom, fileName, duration):
        if zoom <= 0:
            return -1
        if len(dataArr) > 0:
            imgArr = []
            for imgItemDataArr in dataArr:
                img = Image.new("RGBA", (16 * zoom, 16 * zoom))

                # 图像生成
                for y in range(0, 16):
                    for x in range(0, 16):
                        i = (y * 16) * 4 + x * 4
                        c = (int(imgItemDataArr[i + 0]), int(imgItemDataArr[i + 1]), int(imgItemDataArr[i + 2]), int(imgItemDataArr[i + 3]))
                        if zoom > 1:
                            # 倍放矩阵色块填充
                            mx = x * zoom
                            my = y * zoom
                            for zy in range(0, zoom):
                                for zx in range(0, zoom):
                                    img.putpixel((mx + zx, my + zy), c)
                        else:
                            img.putpixel((x, y), c)
                imgArr.append(img)

            if len(imgArr) > 0:
                imageio.mimsave(fileName, imgArr, 'GIF', duration=duration)
                return 0 #处理成功
        return 1 #非GIF图片

pixel = pixelutils()