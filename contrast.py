import cv2


def BrightnessContrast(brightness=0):
    brightness = cv2.getTrackbarPos('Brightness', 'Edit')
    contrast = cv2.getTrackbarPos('Contrast', 'Edit')
    effect = controller(img, brightness, contrast)
    cv2.imshow('Edit', effect)


def controller(img, brightness=255, contrast=127):
    brightness = int((brightness - 0) * (255 - (-255)) / (510 - 0) + (-255))
    contrast = int((contrast - 0) * (127 - (-127)) / (254 - 0) + (-127))
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

    if contrast != 0:
        alpha = float(131 * (contrast + 127)) / (127 * (131 - contrast))
        gamma = 127 * (1 - alpha)
        cal = cv2.addWeighted(cal, alpha, cal, 0, gamma)

    return cal

if __name__ == '__main__':
    """
    Source: https://www.geeksforgeeks.org/changing-the-contrast-and-brightness-of-an-image-using-python-opencv/
    """
    # original = cv2.imread("62034.jpg")
    # img = original.copy()
    # cv2.namedWindow('Edit')
    # cv2.imshow('Edit', original)

    # cv2.createTrackbar('Brightness',
    #                 'Edit', 255, 2 * 255,
    #                 BrightnessContrast)
    # cv2.createTrackbar('Contrast', 'Edit',
    #                 127, 2 * 127,
    #                 BrightnessContrast)
    # cv2.createButton("White Correction",lambda x:x,None,cv2.QT_PUSH_BUTTON,1)
    # BrightnessContrast(0)
    # from tkinter import *
    # window = Tk()
    # w1 = Scale(window, from_=0, to=200, orient=HORIZONTAL)
    # w1.place(x=10, y=60)
    # w2 = Scale(window, from_=0, to=200, orient=HORIZONTAL)
    # w2.place(x=10, y=30)

    # mainloop()
    from tkinter import *
    import tkinter as tk
    from tkinter import ttk
    from ttkwidgets import TickScale


class EditImageWindow:
    def __init__(self) -> None:
        self.top = Tk()
        self.top.geometry("450x800")
        self.top.title('Image Adjustment')
        slider_width = 30
        slider_height = 15
        self.img_slider = tk.PhotoImage('img_slider', width=slider_width, height=slider_height, master=self.top)
        self.set_img_color(self.img_slider, "#ff0000")
        self.img_slider_active = tk.PhotoImage('img_slider_active', width=slider_width, height=slider_height,
                                          master=self.top)
        self.set_img_color(self.img_slider_active, '#1065BF')
        self.configure()
        self.top.mainloop()

    def configure(self):
        """
        Source: https://stackoverflow.com/questions/59642558/how-to-set-tkinter-scale-sliders-color
        """
        self.top.configure(background='#f4f0ec')
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
        Label(self.top, text='Brightness').place(x=10, y=30)
        scale = TickScale(self.top, from_=-255, to=255, tickinterval=255, orient="horizontal",
                        style='custom.Horizontal.TScale', length=300)
        scale.set(0)
        scale.place(x=100, y=10)
        Label(self.top, text='Contrast').place(x=10, y=90)
        scale2 = TickScale(self.top, from_=-255, to=255, tickinterval=255, orient="horizontal",
                        style='custom.Horizontal.TScale', length=300)
        scale2.set(0)
        scale2.place(x=100, y=70)
        Label(self.top, text='Hue').place(x=10, y=150)
        scale3 = TickScale(self.top, from_=-180, to=180, tickinterval=180, orient="horizontal",
                           style='custom.Horizontal.TScale', length=300)
        scale3.set(0)
        scale3.place(x=100, y=130)
        Label(self.top, text='Saturation').place(x=10, y=210)
        scale4 = TickScale(self.top, from_=-100, to=100, tickinterval=100, orient="horizontal",
                           style='custom.Horizontal.TScale', length=300)
        scale4.set(0)
        scale4.place(x=100, y=190)

    def set_img_color(self, img, color):
        pixel_line = "{" + " ".join(color for i in range(img.width())) + "}"
        pixels = " ".join(pixel_line for i in range(img.height()))
        img.put(pixels)


EditImageWindow()


def whitebalance(img):
    r, g, b = cv2.split(img)
    r_avg = cv2.mean(r)[0]
    g_avg = cv2.mean(g)[0]
    b_avg = cv2.mean(b)[0]
    k = (r_avg + g_avg + b_avg)/3

    kr = k/r_avg
    kg = k/g_avg
    kb = k/b_avg

    r = cv2.addWeighted(src1=r, alpha=kr, src2=0, beta=0, gamma=0)
    g = cv2.addWeighted(src1=g, alpha=kg, src2=0, beta=0, gamma=0)
    b = cv2.addWeighted(src1=b, alpha=kb, src2=0, beta=0, gamma=0)
    balance_img = cv2.merge([b, g, r])
    return balance_img
