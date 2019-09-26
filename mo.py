from tkinter import *
from camera import *


class Example(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent
        self.initUI()

    def initUI(self):
        self.pack(expand=1, fill=BOTH)
        self.btn_switch_left = Button(self, text="Вкл/выкл лучи левой камеры", width=50)
        self.c = Canvas(self, width=230)   # Чистый холст
        self.text = Text(self)             # Поле вывода информации
        self.c.pack(side=LEFT, fill=Y, expand=0)
        self.text.pack(side=RIGHT, expand=1, fill=BOTH)

        self.static_ball = self.c.create_oval(117, 12, 123, 18, fill='black')
        self.moving_ball = self.c.create_oval(27, 87, 33, 93, fill='green')

        # Границы
        self.c.create_line(15, 0, 15, 1000, fill='black', width=2)
        self.c.create_line(225, 0, 225, 1000, fill='black', width=2)

        # Изображение камер
        self.c.create_rectangle(5, 1000, 25, 1020)
        self.c.create_rectangle(110, 1000, 130, 1020)
        self.c.create_rectangle(215, 1000, 235, 1020)

        self.c.focus_set()
        self.c.bind('<Left>', self.move_left)
        self.c.bind('<Right>', self.move_right)
        self.camera_vision()

    def move_right(self, event):
        if self.c.coords(self.moving_ball)[2] <= 225:
            self.c.move(self.moving_ball, 1.5, 0)
            self.camera_vision()
            self.change_data()

    def move_left(self, event):
        if self.c.coords(self.moving_ball)[0] >= 15:
            self.c.move(self.moving_ball, -1.5, 0)
            self.camera_vision()
            self.change_data()

    def camera_vision(self):
        def eq_line(x1, y1, x2, y2):
            try:
                k = (y2 - y1) / (x2 - x1)
            except ZeroDivisionError:
                k = 0
            b = y1 - k * x1
            return k, b

        def point_triangle(ax, ay, bx, by, cx, cy, rx, ry):
            """

            :param ax: x-coord of 1st point of triangle
            :param ay: y-coord of 1st point of triangle
            :param bx: x-coord of 2nd point of triangle
            :param by: y-coord of 2nd point of triangle
            :param cx: x-coord of 3rd point of triangle
            :param cy: y-coord of 3rd point of triangle
            :param rx: x-coord of point
            :param ry: y-coord of point
            :return: True - if point inside triangle or False if don't
            """
            n1 = (by - ay) * (rx - ax) - (bx - ax) * (ry - ay)
            n2 = (cy - by) * (rx - bx) - (cx - bx) * (ry - by)
            n3 = (ay - cy) * (rx - cx) - (ax - cx) * (ry - cy)
            if (n1 > 0 and n2 > 0 and n3 > 0) or (n1 < 0 and n2 < 0 and n3 < 0):
                return True
            else:
                return False

        # mb - moving ball, sb - static ball
        mb_left_x = self.c.coords(self.moving_ball)[0]
        mb_left_y = self.c.coords(self.moving_ball)[1] + 3
        mb_right_x = self.c.coords(self.moving_ball)[2]
        mb_right_y = self.c.coords(self.moving_ball)[3] - 3
        self.mb_center_x = mb_left_x + 3
        mb_center_y = mb_left_y + 3

        sb_left_x = self.c.coords(self.static_ball)[0]
        sb_left_y = self.c.coords(self.static_ball)[1] + 3
        sb_right_x = self.c.coords(self.static_ball)[2]
        sb_right_y = self.c.coords(self.static_ball)[3] - 3
        self.sb_center_x = sb_left_x + 3
        sb_center_y = sb_left_y + 3

        # left camera
        zero_point_x = 15
        zero_point_y = 1000
        try:
            for i in self.line_left:
                self.c.delete(i)
        except AttributeError:
            pass

        if point_triangle(zero_point_x, zero_point_y, sb_left_x, sb_left_y, sb_right_x, sb_right_y, mb_right_x,
                          mb_right_y):
            self.left_ray_coord = [[(mb_left_x + sb_right_x) / 2, 900]]
            k, b = eq_line(zero_point_x, zero_point_y, (mb_left_x + sb_right_x) / 2, (mb_left_y + sb_right_y) / 2)
            self.line_left = [self.c.create_line(zero_point_x, zero_point_y, 140, 140 * k + b, dash=(2, 2))]

        elif point_triangle(zero_point_x, zero_point_y, sb_left_x, sb_left_y, sb_right_x, sb_right_y, mb_left_x,
                            mb_left_y):
            self.left_ray_coord = [[(mb_right_x + sb_left_x) / 2, 900]]
            k, b = eq_line(zero_point_x, zero_point_y, (mb_right_x + sb_left_x) / 2, (mb_right_y + sb_left_y) / 2)
            self.line_left = [self.c.create_line(zero_point_x, zero_point_y, 140, 140 * k + b, dash=(2, 2))]

        elif point_triangle(zero_point_x, zero_point_y, sb_left_x, sb_left_y, sb_right_x, sb_right_y, self.mb_center_x,
                            mb_center_y):
            self.left_ray_coord = [[self.mb_center_x, 900]]
            self.line_left = [self.c.create_line(zero_point_x, zero_point_y, self.mb_center_x, mb_center_y, dash=(2, 2))]

        else:
            self.left_ray_coord = [[self.mb_center_x, 900], [self.sb_center_x, 990]]
            self.line_left = [self.c.create_line(zero_point_x, zero_point_y, self.mb_center_x, mb_center_y, dash=(2, 2)),
                              self.c.create_line(zero_point_x, zero_point_y, self.sb_center_x, sb_center_y, dash=(2, 2))]

        # central camera
        zero_point_x = 120
        try:
            for i in self.line_center:
                self.c.delete(i)
        except AttributeError:
            pass

        if self.mb_center_x < zero_point_x:
            z = 105
        elif self.mb_center_x == zero_point_x:
            z = self.mb_center_x
        else:
            z = 140
        if point_triangle(zero_point_x, zero_point_y, sb_left_x, sb_left_y, sb_right_x, sb_right_y, mb_right_x,
                          mb_right_y):
            self.central_ray_coord = [[(mb_left_x + sb_right_x) / 2, 900]]
            k, b = eq_line(zero_point_x, zero_point_y, (mb_left_x + sb_right_x) / 2, (mb_left_y + sb_right_y) / 2)
            self.line_center = [self.c.create_line(zero_point_x, zero_point_y, z, z * k + b, dash=(2, 2), fill='red')]

        elif point_triangle(zero_point_x, zero_point_y, sb_left_x, sb_left_y, sb_right_x, sb_right_y, mb_left_x,
                            mb_left_y):
            self.central_ray_coord = [[(mb_right_x + sb_left_x) / 2, 900]]
            k, b = eq_line(zero_point_x, zero_point_y, (mb_right_x + sb_left_x) / 2, (mb_right_y + sb_left_y) / 2)
            self.line_center = [self.c.create_line(zero_point_x, zero_point_y, z, z * k + b, dash=(2, 2), fill='red')]

        elif point_triangle(zero_point_x, zero_point_y, sb_left_x, sb_left_y, sb_right_x, sb_right_y, self.mb_center_x,
                            mb_center_y):
            self.central_ray_coord = [[self.mb_center_x, 900]]
            self.line_center = [self.c.create_line(zero_point_x, zero_point_y, self.mb_center_x, mb_center_y, dash=(2, 2),
                                                   fill='red')]

        else:
            self.central_ray_coord = [[self.mb_center_x, 900], [self.sb_center_x, 990]]
            self.line_center = [self.c.create_line(zero_point_x, zero_point_y, self.mb_center_x, mb_center_y, dash=(2, 2),
                                                   fill='red'), self.c.create_line(zero_point_x, zero_point_y,
                                                                                   self.sb_center_x, sb_center_y,
                                                                                   dash=(2, 2), fill='red')]

        # right camera
        zero_point_x = 225
        try:
            for i in self.line_right:
                self.c.delete(i)
        except AttributeError:
            pass

        if point_triangle(zero_point_x, zero_point_y, sb_left_x, sb_left_y, sb_right_x, sb_right_y, mb_right_x,
                          mb_right_y):
            self.right_ray_coord = [[(mb_left_x + sb_right_x) / 2, 900]]
            k, b = eq_line(zero_point_x, zero_point_y, (mb_left_x + sb_right_x) / 2, (mb_left_y + sb_right_y) / 2)
            self.line_right = [self.c.create_line(zero_point_x, zero_point_y, 105, 105 * k + b, dash=(2, 2),
                                                  fill='green')]

        elif point_triangle(zero_point_x, zero_point_y, sb_left_x, sb_left_y, sb_right_x, sb_right_y, mb_left_x,
                            mb_left_y):
            self.right_ray_coord = [[(mb_right_x + sb_left_x) / 2, 900]]
            k, b = eq_line(zero_point_x, zero_point_y, (mb_right_x + sb_left_x) / 2, (mb_right_y + sb_left_y) / 2)
            self.line_right = [self.c.create_line(zero_point_x, zero_point_y, 105, 105 * k + b, dash=(2, 2),
                                                  fill='green')]

        elif point_triangle(zero_point_x, zero_point_y, sb_left_x, sb_left_y, sb_right_x, sb_right_y, self.mb_center_x,
                            mb_center_y):
            self.right_ray_coord = [[self.mb_center_x, 900]]
            self.line_right = [self.c.create_line(zero_point_x, zero_point_y, self.mb_center_x, mb_center_y, dash=(2, 2),
                                                  fill='green')]

        else:
            self.right_ray_coord = [[self.mb_center_x, 900], [self.sb_center_x, 990]]
            self.line_right = [self.c.create_line(zero_point_x, zero_point_y, self.mb_center_x, mb_center_y, dash=(2, 2),
                                                  fill='green'), self.c.create_line(zero_point_x, zero_point_y,
                                                                                    self.sb_center_x, sb_center_y,
                                                                                    dash=(2, 2), fill='green')]

    def change_data(self):
        """
        Калибровочные данные инициализации камер для высоты 5400
        """
        left_camera = Camera(2844, 2325, 1267, 725,
                             0.018518518518518517, 0.07407407407407407, 0.18518518518518517, 0.24074074074074073)
        central_camera = Camera(2841, 2320, 1280, 759,
                                0.1111111111111111, 0.05555555555555555, -0.05555555555555555, -0.1111111111111111)
        right_camera = Camera(2875, 2333, 1275, 756,
                              0.24074074074074073, 0.18518518518518517, 0.07407407407407407, 0.018518518518518517)

        # Формирование данных камеры, детектируюя положение луча центра объекта
        left_camera.data = [pixel_in_camera(10*x[1]/1.5, x[0], -700) for x in self.left_ray_coord]
        right_camera.data = [pixel_in_camera(10*x[1]/1.5, x[0], 700) for x in self.right_ray_coord]
        central_camera.data = [pixel_in_camera(10*x[1]/1.5, x[0], 0) for x in self.central_ray_coord]

        detection_wires = bypass(left_camera, central_camera, right_camera)

        self.new_text(self.text, 1.0, "Координаты подвижного провода: H - {0}, L - {1}\n".format(6000,
                                                                            int(10*abs(120 - self.mb_center_x)/1.5)))
        self.new_text(self.text, 2.0, "\nКоординаты статичного провода: H - {0}, L - {1}".format(6600, 0))
        self.new_text(self.text, 3.0, "\nОбнаруженных объектов = {0}".format(detection_wires))
        self.new_text(self.text, 4.0, "\nКоличество объектов левой камеры - {}".format(len(left_camera.data)))
        self.new_text(self.text, 5.0, "\nКоличество объектов центральной камеры - {}".format(len(central_camera.data)))
        self.new_text(self.text, 6.0, "\nКоличество объектов правой камеры - {}".format(len(right_camera.data)))

    def new_text(self, widget, row, text):
        widget.delete(row, END)
        widget.insert(row, text)

def main():
    root = Tk()
    ex = Example(root)
    root.geometry("480x1020")
    root.mainloop()


if __name__ == '__main__':
    main()
