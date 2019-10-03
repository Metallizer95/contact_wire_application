from math import sqrt
import tkinter as tk

height = 600
width = 800
def in_circle(x, y, radius, a, b):
    """
    :param x: center coordinate of circle
    :param y: center coordinate of circle
    :param radius: circle radius
    :param a: x coordinate of some point
    :param b: y coordinate of some point
    :return: True if point is in the circle or False if is not
    """
    if (x - a) ** 2 + (y - b) ** 2 <= radius ** 2:
        return True
    else:
        return False


def all_point_circle(x, y, radius):
    """
    :param x: center coordinate of circle
    :param y: center coordinate of circle
    :param radius: circle radius
    :return: points y axes depend of x
    """
    points_x = list()
    points_y = dict()
    z = x - radius
    while z <= x + radius:
        points_x.append(z)
        z += 1
    for i in points_x:
        a = 1
        b = -2 * y
        c = i**2 - 2*i*x + x**2 + y**2 - radius**2
        points_y[i] = solve_square_equal(a, b, c)
    print(len(points_y))
    return points_y


def point_in_circle(circle, k, b):
    x = circle[0]
    y = circle[1]
    radius = circle[2]
    yPoints = all_point_circle(x, y, radius)
    xLine = list()
    yLine = list()
    z = x - radius
    while z <= x + radius:
        xLine.append(z)
        z += 1
    point = 0
    for i in yPoints.keys():
        yLine.append(k*xLine[point] + b)
        if len(yPoints[i]) == 1:
            if round(yPoints[i][0]) == round(yLine[point]):
                return [True,  yPoints[i][0]]
        else:
            if min(yPoints[i]) <= yLine[point] <= max(yPoints[i]):
                return [True, min(yPoints[i])]
        point += 1
    return [False]

def solve_square_equal(a, b, c):
    """
    :param a: coefficient of square multiplier
    :param b: coefficient of single multiplier
    :param c: free multiplier
    :return: solving of square equal
    """
    D = b ** 2 - 4 * a * c
    if D < 0:
        return False
    elif D == 0:
        return [-b / (2 * a)]
    else:
        return [(-b + sqrt(D)) / (2 * a), (-b - sqrt(D)) / (2 * a)]


def equationLine(x1, y1, x2, y2):
    try:
        k = (y2 - y1) / (x2 - x1)
    except ZeroDivisionError:
        k = 0
    b = y1 - k * x1
    return k, b


class Create_Canvas(tk.Canvas):
    def __init__(self, parent=None, **config):
        tk.Canvas.__init__(self, parent, **config)
        self.all_camera = dict()  # Хранит информацию обо всех камерах
        self.all_circles = dict()

    def create_circle(self, center_x, center_y, radius, **config):
        center_y = height - center_y
        circle = self.create_oval(center_x - radius, center_y - radius, center_x + radius, center_y + radius, **config)
        self.all_circles[circle] = [center_x, center_y, radius]
        return circle

    def create_camera(self, center_x, center_y, radius, **config):
        center_y = height - center_y
        camera = self.create_rectangle(center_x - radius, center_y - radius, center_x + radius, center_y + radius, **config)
        self.all_camera[camera] = [center_x, center_y, radius]
        return camera

    def rays_of_camera(self):
        for camera in self.all_camera.keys():
            zero_x = self.all_camera[camera][0]
            zero_y = self.all_camera[camera][1] - self.all_camera[camera][2]
            ray_y = zero_y - 500
            left_ray_x = zero_x - 500 * 1.71  # 1.71 - tg60 = sqrt(3)
            right_ray_x = zero_y + 500 * 1.71
            while left_ray_x <= right_ray_x:
                k, b = equationLine(zero_x, zero_y, left_ray_x, ray_y)
                test = point_in_circle(self.all_circles[1], k, b)
                if not test[0]:
                    self.create_line(zero_x, zero_y, left_ray_x, ray_y, fill='yellow')
                else:
                    self.create_line(zero_x, zero_y, left_ray_x, test[1])
                left_ray_x += 4


class Create_Frame(tk.Frame):
    def __init__(self, parent=None):
        tk.Frame.__init__(self, parent)
        self.pack()
        canvas = Create_Canvas(width=width, height=height)
        canvas.pack()
        canvas.create_circle(200, 400, 40, fill='red')
        canvas.create_camera(300, 10, 10)
        canvas.rays_of_camera()


if __name__ == '__main__':
    root = tk.Tk()
    ex = Create_Frame()
    root.geometry(str(width)+"x"+str(height))
    root.mainloop()
