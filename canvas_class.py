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
    def __init__(self, points, angle):
        self.top_left = points[0]
        self.top_right = points[1]
        self.bot_right = points[2]
        self.bot_left = points[3]
        self.angle = angle
        self.xRightRay = None
        self.xLeftRay = None

        # Набор лучей
        self.coefs = {}
        self.delta = 0.008*SCALE   # Шаг луча

        # Точка фокуса
        self.zero_x = (self.top_left[0] + self.top_right[0])/2
        self.zero_y = (self.top_left[1] + self.top_right[1])/2
        
        #  Конечная точка луча
        self.yLeftRay = self.bot_right[1]
        self.xLeftRay = self.bot_right[0]

        self.yRightRay = self.bot_left[1]
        self.xRightRay = self.bot_left[0]


class Wire_object:
    def __init__(self, x, y, r):
        self.x = START + x*SCALE + WIDTH/2
        self.y = MAX_H - y*SCALE
        self.r = r*SCALE
        self.all_data = [self.x, self.y, self.r]
        print(self.all_data)

    def change_data(self, x, y):
        self.x = x
        self.y = y
        self.all_data[0] = x
        self.all_data[1] = y

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

        camera = Camera_object(new_points, angle)
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
        yRay = camera.yLeftRay
        coefs = {}
        x_offset = math.cos(math.radians(camera.angle))*camera.delta
        y_offset = math.sin(math.radians(camera.angle))*camera.delta
        iteration_var = 0
        while round(xLeftRay, 3) > round(xRightRay, 3):
            coefs[iteration_var] = mf.equationLine(camera.zero_x, camera.zero_y, xLeftRay, yRay)
            xLeftRay -= x_offset
            yRay -= y_offset
            iteration_var += 1
        print(iteration_var)
        return coefs
