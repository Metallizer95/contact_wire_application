import tkinter as tk
import math_functions as mf
import math

SCALE = 0.15
START = 15
WIDTH = 1400 * SCALE
MAX_H = 6800 * SCALE

class Camera_object:
    def __init__(self, cordx, cordy, width, height):
        self.cordx = START + cordx * SCALE + WIDTH / 2
        self.cordy = MAX_H - cordy * SCALE
        self.width = width * SCALE
        self.height = height * SCALE
        # Набор лучей
        self.tg11 = 0.19456
        self.zero_x = self.cordx
        self.zero_y = self.cordy
        self.yRay = self.zero_y - 1000
        self.xLeftRay = self.zero_x - 1000*self.tg11
        self.xRightRay = self.zero_x + 1000*self.tg11

    def write_center(self, x, y):
        self.zero_x = x
        self.zero_y = y
        self.xLeftRay = self.zero_x - 1000 * self.tg11
        self.xRightRay = self.zero_x + 1000 * self.tg11

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
        camera = Camera_object(cordx, cordy, width, height)
        points_left_top = [camera.cordx - camera.width/2, camera.cordy - camera.height]
        points_right_top = [camera.cordx + camera.width/2, camera.cordy - camera.height]
        points_left_bot = [camera.cordx - camera.width/2, camera.cordy]
        points_right_bot = [camera.cordx + camera.width/2, camera.cordy]
        center = [camera.cordx, camera.cordy - camera.height/2]
        new_points = self.rotate([points_left_top, points_right_top, points_right_bot, points_left_bot ], angle, center)
        camera.write_center((new_points[0][0] + new_points[1][0])/2, (new_points[0][1] + new_points[1][1])/2)
        return self.create_polygon(new_points, **config), camera

    def create_circle(self, x, y, r, **config):
        circle = Wire_object(x, y, r)
        x_left = circle.x - circle.r
        y_left = circle.y - circle.r
        x_right = circle.x + circle.r
        y_right = circle.y + circle.r
        return self.create_oval(x_left, y_left, x_right, y_right, **config), circle

    @staticmethod
    def rotate(points, angle, center):
        angle = math.radians(angle)
        cos_val = math.cos(angle)
        sin_val = math.sin(angle)
        cx, cy = center
        new_points = []
        for x_old, y_old in points:
            x_old -= cx
            y_old -= cy
            x_new = x_old*cos_val - y_old*sin_val
            y_new = x_old*sin_val + y_old*cos_val
            new_points.append([x_new + cx, y_new + cy])
        return new_points

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
