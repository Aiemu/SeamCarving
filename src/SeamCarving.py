import sys
import time
import threading
import argparse
import cv2
import numpy as np
import matplotlib  
import matplotlib.pyplot as plt

from skimage import color, io, util
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QColor, QPixmap
from PyQt5.QtCore import Qt

from GUI import *

matplotlib.use('Qt5Agg')
rtime = time.time();
timeout = False;
delta = 1;

# class to manage GUI pages
class Pages:
    def __init__(self):
        self.pageMain = Ui_pageMain()

# class to manage main window
class PageMain(QtWidgets.QMainWindow):
    resized = QtCore.pyqtSignal()
    def __init__(self, mH, mW):
        super(PageMain, self).__init__()
        self.setMaximumSize(2 * mW - 1, 2 * mH - 1)

    # resize event
    def resizeEvent(self, event):
        global rtime, timeout, delta
        rtime = time.time()
        if not timeout:
            timeout = True;
            timethread = threading.Timer(delta, self.resizeEnd)
            timethread.start()
        return super(QtWidgets.QMainWindow, self).resizeEvent(event)

    # set timeout to prevent crash for to many resize operations
    def resizeEnd(self):
        global rtime, timeout, delta
        if time.time() - rtime < delta:
            timethread = threading.Timer(delta, self.resizeEnd)
            timethread.start()
        else:
            timeout = False;
            self.resized.emit()

# class to process seam carving
class SeamCarving():
    img_name = ""

    def __init__(self, img_name, EF=0):
        self.img_name = img_name
        if EF == 0:
            self.enFunc = self.energyFunc
        elif EF == 1:
            self.enFunc = self.energyFuncSaliency

    # main process to resize image
    def resizeImg(self, pages, win_size):
        im = io.imread('imgs/input/' + self.img_name)
        im = util.img_as_float(im)

        ret = im;

        # resize width
        if win_size.width() > im.shape[1]:
            ret = self.sizeUp(im, win_size.width(), 1)
        elif win_size.width() < im.shape[1]:
            ret = self.sizeDown(im, win_size.width(), 1)

        # resize height
        if win_size.height() > im.shape[0]:
            ret = self.sizeUp(ret, win_size.height(), 0)
        elif win_size.height() < im.shape[0]:
            ret = self.sizeDown(ret, win_size.height(), 0)

        # save result
        plt.imsave('imgs/output/carved_' + self.img_name, ret)

        # show result
        pix = QPixmap('imgs/output/carved_' + self.img_name)
        pages.pageMain.label.setGeometry(0, 0, pix.size().width(), pix.size().height())
        pages.pageMain.label.setPixmap(pix)

    # shrink the image in 2 directions
    def sizeDown(self, image, size, direction):
        ret = np.copy(image)

        # rotate
        if direction == 0:
            ret = np.transpose(ret, (1, 0, 2))

        # to del
        while ret.shape[1] > size:
            ener = self.enFunc(ret)
            losses, pos = self.enLoss(ret, ener)
            end = np.argmin(losses[-1])
            seam = self.searchSeam(pos, end)
            ret = self.delSeam(ret, seam)

        # re-rotate
        if direction == 0:
            ret = np.transpose(ret, (1, 0, 2))

        return ret

    # expand the image in 2 directions
    def sizeUp(self, image, size, direction):
        ret = np.copy(image)

        # rotate
        if direction == 0:
            ret = np.transpose(ret, (1, 0, 2))

        H, W, C = ret.shape

        # to add
        seams = self.getSeam(ret, size - W)
        for i in range(0, size - W):
            seam = np.where(seams == i + 1)[1]
            ret = self.addSeam(ret, seam)

        # re-rotate
        if direction == 0:
            ret = np.transpose(ret, (1, 0, 2))

        return ret

    # get the seam
    def searchSeam(self, pos, end):
        H, W = pos.shape
        seam = - np.ones(H, dtype=np.int)

        seam[H - 1] = end

        for h in range(H - 1, 0, -1):
            seam[h - 1] = seam[h] + pos[h, end]
            end += pos[h, end]

        return seam

    # del seam from image to shrink it
    def delSeam(self, image, seam):
        if len(image.shape) == 2:
            image = np.expand_dims(image, axis=2)

        H, W, C = image.shape

        mask_img = np.ones_like(image, bool)
        for h in range(0, H):
            mask_img[h, seam[h]] = False
        ret = image[mask_img].reshape(H, W - 1, C)
        ret = np.squeeze(ret)

        return ret

    # add seam into image to expand it
    def addSeam(self, image, seam):
        if len(image.shape) == 2:
            image = np.expand_dims(image, axis=2)

        H, W, C = image.shape
        ret = np.zeros((H, W + 1, C))

        for h in range(0, H):
            ret[h] = np.vstack((image[h, :seam[h]], image[h, seam[h]], image[h, seam[h]:]))

        return ret

    # get the seam which has the lowest energy
    def getSeam(self, image, k):
        image = np.copy(image)

        H, W, C = image.shape
        index_list = np.tile(range(0, W), (H, 1))
        seams = np.zeros((H, W), dtype=np.int)

        for i in range(0, k):
            # init
            ener = self.enFunc(image)
            loss, pos = self.enLoss(image, ener)
            end = np.argmin(loss[H - 1])
            seam = self.searchSeam(pos, end)

            # del seam
            image = self.delSeam(image, seam)

            # save img
            tmp = index_list[np.arange(H), seam]
            seams[np.arange(H), tmp] = i + 1
            index_list = self.delSeam(index_list, seam)

        return seams

    # gradient energy function 
    def energyFunc(self, image):
        # trans into gray
        gray_image = color.rgb2gray(image)

        # compute energy_map
        gradient = np.gradient(gray_image)
        energy_map = np.absolute(gradient[0]) + np.absolute(gradient[1])
        return energy_map

    # saliency measure energy function 
    def energyFuncSaliency(self, image):
        # trans into gray
        gray_image = color.rgb2gray(image)

        # compute energy_map
        saliency = cv2.saliency.StaticSaliencySpectralResidual_create()
        (_, energy_map) = saliency.computeSaliency(gray_image)
        return energy_map

    # get the energy loss
    def enLoss(self, image, ener):
        ener = ener.copy()
        H, W = ener.shape

        loss = np.zeros((H, W))
        pos = np.zeros((H, W), dtype=np.int)
        loss[0] = ener[0]
        pos[0] = 0

        for row in range(1, H):
            top_l = np.insert(loss[row - 1, 0:W - 1], 0, 1e10, axis=0)
            top_m = loss[row - 1, :]
            top_r = np.insert(loss[row - 1, 1:W], W - 1, 1e10, axis=0)
            remains = np.concatenate((top_l, top_m, top_r), axis=0).reshape(3, -1)

            loss[row] = ener[row] + np.min(remains, axis=0)
            pos[row] = np.argmin(remains, axis=0) - 1
        return loss, pos


if __name__ == "__main__":
    # get params
    parser = argparse.ArgumentParser(description='Process some integers.')

    parser.add_argument('-i', '--image', required=True, help='choose image in ./imgs/input/')

    parser.add_argument('-e', '--energyfunction', default=0, type=int, help='choose energy function, 0: gradient, 1: saliency measure. Default: 0')

    parser.add_argument('-W', '--width', type=int, help='set the width of result and output the result directly.')

    parser.add_argument('-H', '--height', type=int, help='set the height of result and output the result directly.')

    flag = True
    args = parser.parse_args()
    if args.width or args.height or args.width == 0 or args.height == 0:
        flag = False

    # read in img
    img_name = args.image
    im = io.imread('imgs/input/' + img_name)
    im = util.img_as_float(im)
    plt.imsave('imgs/output/carved_' + img_name, im)

    # init seam carving obj
    SC = None 
    if args.energyfunction or args.energyfunction == 0:
        SC = SeamCarving(img_name, args.energyfunction)
    else:
        SC = SeamCarving(img_name)

    if flag: # show with GUI
        # init window
        pages = Pages()
        app = QApplication(sys.argv)

        # set max size
        pageMain = PageMain(im.shape[0], im.shape[1])

        # set up UI and disp
        pages.pageMain.setupUi(pageMain)
        pageMain.show()

        # bind signal
        pageMain.resized.connect(lambda: SC.resizeImg(pages, pageMain.size()))

        # save ori img and disp in window
        pix = QPixmap('imgs/output/carved_' + img_name)
        pages.pageMain.label.setGeometry(0, 0, pix.size().width(), pix.size().height())
        pages.pageMain.label.setPixmap(pix)
        pageMain.resize(pix.size())

        sys.exit(app.exec_())
    else: # output
        out_flag = True
        ret = im
        if args.width and args.width > 0 and args.width <= 2 * im.shape[1] - 1:
            out_flag = False
            if args.width > im.shape[1]:
                print("Resizing...")
                ret = SC.sizeUp(im, args.width, 1)
            elif args.width < im.shape[1]:
                print("Resizing...")
                ret = SC.sizeDown(im, args.width, 1)
            plt.imsave("imgs/output/carved_" + img_name, ret)

        if args.height and args.height > 0 and args.height <= 2 * im.shape[0] - 1:
            out_flag = False
            if args.height > im.shape[0]:
                print("Resizing...")
                ret = SC.sizeUp(ret, args.height, 0)
            elif args.height < im.shape[0]:
                print("Resizing...")
                ret = SC.sizeDown(ret, args.height, 0)
            plt.imsave("imgs/output/carved_" + img_name, ret)

        if (args.width and args.width > 2 * im.shape[1] - 1) or (args.height and args.height > 2 * im.shape[0] - 1):
            out_flag = False
            print("Error: Target image is too large.")
        else:
            if out_flag:
                print("Error: Please check the format of parameter.")
            else: 
                print("Complete, bye!")