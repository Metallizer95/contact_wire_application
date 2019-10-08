from math import sqrt
import tkinter as tk

height = 1000
width = 800

def check_line_in_circle(circle, kLine, bLine):
    a = circle[0]
    b = circle[1]
    k = kLine
    d = bLine
    r = circle[2]

    xq = 1 + k**2
    x = -2*a + 2*k*d - 2*k*b
    fx = a**2 + d**2 + b**2 - 2*b*d - r**2
    solve = solve_square_equal(xq, x, fx)
    if not solve:
        return solve
    elif len(solve) == 1:
        return 1, solve[0], k*solve[0] + d
    else:
        y1 = solve[0] * k + d
        y2 = solve[1] * k + d
        yMin = max(y1, y2)
        xMin = (yMin - d)/k
        return 2, xMin, yMin

def solve_square_equal(a, b, c):
    """
    :param a: coefficient of square multiplier
    :param b: coefficient of single multiplier
    :param c: free multiplier
    :return: solving of square equal
    """
    D = b**2 - 4*a*c
    if D < 0:
        return False
    elif round(D, 2) == 0:
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

            draw_points = set()
            solve = set()
            while left_ray_x <= right_ray_x:
                k, b = equationLine(zero_x, zero_y, left_ray_x, ray_y)
                if k == 0:
                    left_ray_x += 0.001
                    continue
                for key in self.all_circles:
                    solve.add(check_line_in_circle(self.all_circles[key], k, b))
                left_ray_x += 3

            for i in solve:
                if i:
                    draw_points.add(i)
            for i in draw_points:
                self.create_line(zero_x, zero_y, i[1], i[2], fill='black')


class Create_Frame(tk.Frame):
    def __init__(self, parent=None):
        tk.Frame.__init__(self, parent)
        self.pack()
        canvas = Create_Canvas(width=width, height=height)
        canvas.pack()
        canvas.create_circle(300, 600, 40, fill='red')
        canvas.create_circle(350, 800, 40, fill='red')
        canvas.create_camera(100, 10, 10)
        canvas.create_camera(400, 10, 10)
        canvas.create_camera(700, 10, 10)
        canvas.rays_of_camera()


if __name__ == '__main__':
    root = tk.Tk()
    ex = Create_Frame()
    root.geometry(str(width)+"x"+str(height))
    root.mainloop()
