import threading
import time

import PIL
import cv2
from tkinter import *
import tkinter as tk
from tkinter import ttk

import numpy as np
from PIL import ImageTk
from ttkwidgets import TickScale

STOP_EDIT_FLAG = True


def adjust_brightness(img, brightness):
    brightness += 255
    brightness = int((brightness - 0) * (255 - (-255)) / (510 - 0) + (-255))
    cal = img.copy()
    if brightness != 0:
        if brightness > 0:
            shadow = brightness
            max = 255
        else:
            shadow = 0
            max = 255 + brightness
        alpha = (max - shadow) / 255
        gamma = shadow
        cal = cv2.addWeighted(img, alpha,
                              img, 0, gamma)
    return cal


def adjust_contrast(img, contrast):
    contrast += 127
    contrast = int((contrast - 0) * (127 - (-127)) / (254 - 0) + (-127))
    cal = img.copy()
    if contrast != 0:
        alpha = float(131 * (contrast + 127)) / (127 * (131 - contrast))
        gamma = 127 * (1 - alpha)
        cal = cv2.addWeighted(cal, alpha, cal, 0, gamma)
    return cal


def adjust_hue(img, hue):
    cal = img.copy()
    cal = cv2.cvtColor(cal, cv2.COLOR_BGR2HSV)
    h, s, i = cv2.split(cal)
    h = h + hue
    cal = cv2.merge([h, s, i])
    return cv2.cvtColor(cal, cv2.COLOR_HSV2BGR)


def adjust_sat(img, sat):
    cal = img.copy()
    cal = cv2.cvtColor(cal, cv2.COLOR_BGR2HSV)
    h, s, i = cv2.split(cal)
    s = s + sat
    cal = cv2.merge([h, s, i])
    return cv2.cvtColor(cal, cv2.COLOR_HSV2BGR)


class EditImageWindow:
    def __init__(self):
        global STOP_EDIT_FLAG
        STOP_EDIT_FLAG = False
        self.t1 = threading.Thread(target=self.image_edit_thread)

        self.top = Tk()

        self.img_slider = tk.PhotoImage('img_slider', width=30, height=15, master=self.top)
        self.set_img_color(self.img_slider, "#ff0000")
        self.img_slider_active = tk.PhotoImage('img_slider_active', width=30, height=15, master=self.top)
        self.set_img_color(self.img_slider_active, '#1065BF')

        self.brightness_scale = self.create_tick_scale(255)
        self.contrast_scale = self.create_tick_scale(255)
        self.hue_scale = self.create_tick_scale(180)
        self.sat_scale = self.create_tick_scale(100)
        # self.image = np.zeros((320, 240, 3), np.uint8)
        self.image = cv2.resize(cv2.imread('pras.jpg'), (320, 240))[..., ::-1]
        img_size = (240, 320)
        im = ImageTk.PhotoImage(PIL.Image.fromarray(self.image))
        self.preview_frame = Label(self.top, image=im)
        self.preview_frame.imgtk = im
        self.preview_frame.place(x=125, y=270,
                                 width=img_size[0],
                                 height=img_size[1])

        self.configure()
        self.top.protocol("WM_DELETE_WINDOW", self.stop_edit)
        self.top.mainloop()

    def create_tick_scale(self, x):
        scale = TickScale(self.top, from_=-x, to=x, tickinterval=x, orient="horizontal",
                          style='custom.Horizontal.TScale', length=300)
        scale.set(0)
        return scale

    def configure(self):
        """
        Source: https://stackoverflow.com/questions/59642558/how-to-set-tkinter-scale-sliders-color
        """
        self.top.geometry("450x600")
        self.top.title('Image Adjustment')
        self.top.configure(background='#f4f0ec')
        self.t1.start()

        style = ttk.Style(self.top)
        style.theme_use('clam')
        style.element_create('custom.Horizontal.Scale.slider', 'image', self.img_slider,
                             ('active', self.img_slider_active))
        style.layout('custom.Horizontal.TScale',
                     [('Horizontal.Scale.trough',
                       {'sticky': 'nswe',
                        'children': [('custom.Horizontal.Scale.slider',
                                      {'side': 'left', 'sticky': ''})]})])
        style.configure('custom.Horizontal.TScale', background='#f4f0ec', foreground='#880000',
                        troughcolor='#73B5FA')

        Label(self.top, text='Brightness').place(x=10, y=20)
        self.brightness_scale.place(x=100, y=0)

        Label(self.top, text='Contrast').place(x=10, y=80)
        self.contrast_scale.place(x=100, y=60)

        Label(self.top, text='Hue').place(x=10, y=140)
        self.hue_scale.place(x=100, y=120)

        Label(self.top, text='Saturation').place(x=10, y=200)
        self.sat_scale.place(x=100, y=180)

    def image_edit_thread(self):
        brightness, contrast, hue, sat = [0] * 4
        while True:
            if STOP_EDIT_FLAG:
                print('THREAD TERMINATE SIG')
                break
            if brightness != self.brightness:
                adjust = adjust_brightness(self.image, self.brightness)
                brightness = self.brightness
                self.update_image(adjust)
            if contrast != self.contrast:
                adjust = adjust_contrast(self.image, self.contrast)
                contrast = self.contrast
                self.update_image(adjust)
            if hue != self.hue:
                adjust = adjust_hue(self.image, hue)
                hue = self.hue
                self.update_image(adjust)
            if sat != self.sat:
                adjust = adjust_sat(self.image, self.sat)
                sat = self.sat
                self.update_image(adjust)
            time.sleep(0.5)

    def update_image(self, image):
        image = ImageTk.PhotoImage(PIL.Image.fromarray(image))
        self.preview_frame.imgtk = image
        self.preview_frame.configure(image=image)

    def stop_edit(self):
        global STOP_EDIT_FLAG
        STOP_EDIT_FLAG = True
        self.t1.join()
        self.top.destroy()

    @staticmethod
    def set_img_color(img, color):
        pixel_line = "{" + " ".join(color for i in range(img.width())) + "}"
        pixels = " ".join(pixel_line for i in range(img.height()))
        img.put(pixels)

    @property
    def brightness(self):
        return self.brightness_scale.get()

    @property
    def contrast(self):
        return self.contrast_scale.get()

    @property
    def hue(self):
        return self.hue_scale.get()

    @property
    def sat(self):
        return self.sat_scale.get()


EditImageWindow()
time.sleep(2)
