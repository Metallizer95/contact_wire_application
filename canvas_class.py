import tkinter as tk
import math_functions as mf
import math

SCALE = 0.15
START = 15
WIDTH = 1400 * SCALE
MAX_H = 6800 * SCALE


def rotate(points, angle, center):
    if not angle:
        return points
    angle = math.radians(angle)
    cos_val = math.cos(angle)
    sin_val = math.sin(angle)
    cx, cy = center
    new_points = []
    for x_old, y_old in points:
        x_old -= cx
        y_old -= cy
        x_new = x_old * cos_val - y_old * sin_val
        y_new = x_old * sin_val + y_old * cos_val
        new_points.append([x_new + cx, y_new + cy])
    return new_points

class Camera_object:
    def __init__(self, points):
        self.top_left = points[0]
        self.top_right = points[1]
        self.bot_right = points[2]
        self.bot_left = points[3]
        self.xRightRay = None
        self.xLeftRay = None
        # Набор лучей
        self.zero_x = (self.top_left[0] + self.top_right[0])/2
        self.zero_y = (self.top_left[1] + self.top_right[1])/2
        self.yRay = self.zero_y - 1000
        self.ray_cords()

    def change_center(self, x, y):
        self.zero_x = x
        self.zero_y = y

    def ray_cords(self):
        k1, b1 = mf.equationLine(self.zero_x, self.zero_y, self.bot_left[0], self.bot_left[1])
        k2, b2 = mf.equationLine(self.zero_x, self.zero_y, self.bot_right[0], self.bot_right[1])
        try:
            self.xRightRay = (self.yRay - b1)/k1
        except ZeroDivisionError:
            self.xRightRay = 0
        try:
            self.xLeftRay = (self.yRay - b2)/k2
        except ZeroDivisionError:
            self.xLeftRay = 0

class Wire_object:
    def __init__(self, x, y, r):
        self.x = START + x*SCALE + WIDTH/2
        self.y = MAX_H - y*SCALE
        self.r = r*SCALE
        self.all_data = [self.x, self.y, self.r]

class Canvas_object(tk.Canvas):
    def __init__(self, parent=None, **config):
        tk.Canvas.__init__(self, parent, **config)

    def create_camera(self, cordx, cordy, width, height, angle, **config):
        cordx = START + cordx * SCALE + WIDTH / 2
        cordy = MAX_H - cordy * SCALE
        width = width * SCALE
        height = height * SCALE
        points_left_top = [cordx - width/2, cordy - height]
        points_right_top = [cordx + width/2, cordy - height]
        points_left_bot = [cordx - width/2, cordy]
        points_right_bot = [cordx + width/2, cordy]
        center = [cordx, cordy - height/2]
        new_points = rotate([points_left_top, points_right_top, points_right_bot, points_left_bot], angle, center)

        camera = Camera_object(new_points)
        camera.change_center((new_points[1][0] + new_points[0][0])/2, (new_points[1][1] + new_points[0][1])/2)
        return self.create_polygon(new_points, **config), camera

    def create_circle(self, x, y, r, **config):
        circle = Wire_object(x, y, r)
        x_left = circle.x - circle.r
        y_left = circle.y - circle.r
        x_right = circle.x + circle.r
        y_right = circle.y + circle.r
        return self.create_oval(x_left, y_left, x_right, y_right, **config), circle

    @staticmethod
    def move_ray(camera):
        xLeftRay = camera.xLeftRay
        xRightRay = camera.xRightRay
        yRay = camera.yRay
        coefs = {}
        iteration_var = 0
        while xLeftRay <= xRightRay:
            coefs[iteration_var] = mf.equationLine(camera.zero_x, camera.zero_y, xLeftRay, yRay)
            xLeftRay += 0.10667
            iteration_var += 1
        return coefs