from tkinter import *
from camera import *
SCALE = 0.15
WIDTH = 210  # 1400 * SCALE
START = 15
max_height = 6800 * SCALE

class Text_tk(Text):
    def __init__(self, parent=None, **config):
        Text.__init__(self, parent, **config)

    def new_text(self, row, text):
        self.delete(row, END)
        self.insert(row, text)

class Canvas_ball(Canvas):
    """
    Все размеры принимаются в мм, масштабирование происходит внутри класса
    """
    def __init__(self, parent=None, **config):
        Canvas.__init__(self, parent, width=240, **config)
        self.create_border()
        self.draw_camera()
        self.moving_ball = self.create_circle(100, 6000, 20, fill='green')
        self.static_ball = self.create_circle(700, 6600, 20, fill='black')

    def draw_camera(self):
        half_width_camera = 10
        self.create_rectangle(START - half_width_camera, 1000, START + half_width_camera, 1020)                         # Left camera
        self.create_rectangle(START + WIDTH - half_width_camera, 1000, START + WIDTH + half_width_camera, 1020)         # Right camera
        self.create_rectangle(START + WIDTH/2 - half_width_camera, 1000, START + WIDTH/2 + half_width_camera, 1020)     # Central camera

    def create_border(self):
        self.create_line(START, 0, START, 1000, fill='black', width=2)
        self.create_line(START + WIDTH, 0, START + WIDTH, 1000, fill='black', width=2)

    def create_circle(self, coordx, coordy, radius, **config):
        coordx *= SCALE
        coordy *= SCALE
        radius *= SCALE
        return self.create_oval(START+coordx-radius, max_height-coordy-radius, START+coordx+radius,
                                max_height-coordy+radius, **config)

class Example(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent
        self.canvas = Canvas_ball(self)
        self.information_field = Text_tk(self)
        self.initUI()

    def initUI(self):
        self.pack(expand=1, fill=BOTH)
        self.canvas.pack(side=LEFT, expand=1, fill=Y)
        self.information_field.pack(side=RIGHT, expand=1, fill=BOTH)

        self.canvas.focus_set()

        # Binding buttons
        self.canvas.bind('<Left>', lambda event: self.move_left(self.canvas.moving_ball))
        self.canvas.bind('<Right>', lambda event: self.move_right(self.canvas.moving_ball))
        self.canvas.bind('<Up>', lambda event: self.move_up(self.canvas.moving_ball))
        self.canvas.bind('<Down>', lambda event: self.move_down(self.canvas.moving_ball))
        self.canvas.bind('a', lambda event: self.move_left(self.canvas.static_ball))
        self.canvas.bind('d', lambda event: self.move_right(self.canvas.static_ball))
        self.canvas.bind('w', lambda event: self.move_up(self.canvas.static_ball))
        self.canvas.bind('s', lambda event: self.move_down(self.canvas.static_ball))

        self.dict_lines = {'left': [], 'central': [], 'right': []}
        self.camera_vision()

    def move_right(self, ball):
        if self.canvas.coords(ball)[2] <= START + WIDTH:
            self.canvas.move(ball, 1.5, 0)
            self.camera_vision()
            self.change_data()

    def move_left(self, ball):
        if self.canvas.coords(ball)[0] >= 15:
            self.canvas.move(ball, -1.5, 0)
            self.camera_vision()
            self.change_data()

    def move_up(self, ball):
        if self.canvas.coords(ball)[1] >= 0:
            self.canvas.move(ball, 0, -1.5)
            self.camera_vision()
            self.change_data()

    def move_down(self, ball):
        if self.canvas.coords(ball)[3] <= 210:
            self.canvas.move(ball, 0, 1.5)
            self.camera_vision()
            self.change_data()

    def camera_vision(self):
        def eq_line(x1, y1, x2, y2):
            """
            :param x1: Координата x первой точки
            :param y1: Координата y первой точки
            :param x2: Координата x второй точки
            :param y2: Координата y второй точки
            :return: Возвращает коэффициенты уравнения прямой, построенной по двум точкам
            """
            try:
                k = (y2 - y1) / (x2 - x1)
            except ZeroDivisionError:
                k = 0
            b = y1 - k * x1
            return k, b

        def point_triangle(ax, ay, bx, by, cx, cy, rx, ry):
            """
            :param ax: Координата x 1ой точки треугольника
            :param ay: Координата y 1ой точки треугольника
            :param bx: Координата x 2ой точки треугольника
            :param by: Координата y 2ой точки треугольника
            :param cx: Координата x 3ей точки треугольника
            :param cy: Координата y 3ей точки треугольника
            :param rx: Координата x проверочной точки
            :param ry: Координата y проверочной точки
            :return: Возвращает True, если точки лежит в плоскости, ограниченной треугольником, в иной случае
            возвращает False
            """
            n1 = (by - ay) * (rx - ax) - (bx - ax) * (ry - ay)
            n2 = (cy - by) * (rx - bx) - (cx - bx) * (ry - by)
            n3 = (ay - cy) * (rx - cx) - (ax - cx) * (ry - cy)
            if (n1 > 0 and n2 > 0 and n3 > 0) or (n1 < 0 and n2 < 0 and n3 < 0):
                return True
            else:
                return False

        def draw_raws(zero_point_x, zero_point_y, camera):
            # mb - moving ball, sb - static ball
            if self.canvas.coords(self.canvas.moving_ball)[1] >= self.canvas.coords(self.canvas.static_ball)[1]:
                m_position = self.canvas.coords(self.canvas.moving_ball)
                s_position = self.canvas.coords(self.canvas.static_ball)
            else:
                m_position = self.canvas.coords(self.canvas.static_ball)
                s_position = self.canvas.coords(self.canvas.moving_ball)

            mb_left_x = m_position[0]
            mb_left_y = m_position[1] + 3
            mb_right_x = m_position[2]
            mb_right_y = m_position[3] - 3
            mb_center_y = mb_left_y
            mb_center_x = mb_left_x + 3

            sb_left_x = s_position[0]
            sb_left_y = s_position[1] + 3
            sb_right_x = s_position[2]
            sb_right_y = s_position[3] - 3
            sb_center_x = sb_left_x + 3
            sb_center_y = sb_left_y

            if camera.lower() == 'left':
                endPoint = 210
                color = 'black'
            elif camera.lower() == 'right':
                endPoint = 15
                color = 'green'
            elif camera.lower() == 'central':
                color = 'red'
                if mb_center_x < zero_point_x:
                    endPoint = 15
                elif mb_center_x == zero_point_x:
                    endPoint = mb_center_x
                else:
                    endPoint = 210
            else:
                return False

            for i in self.dict_lines[camera]:
                self.canvas.delete(i)

            if point_triangle(zero_point_x, zero_point_y, sb_left_x, sb_left_y, sb_right_x, sb_right_y,
                              mb_right_x, mb_right_y):

                object_coord = [[(mb_left_x + sb_right_x) / 2 - START - WIDTH/2, max_height - min(sb_center_y,
                                                                                                  mb_center_y)]]
                center_mask_obj = [(mb_left_x + sb_right_x) / 2, (mb_left_y + sb_right_y) / 2]
                k, b = eq_line(zero_point_x, zero_point_y, center_mask_obj[0], center_mask_obj[1])
                self.dict_lines[camera] = [self.canvas.create_line(zero_point_x, zero_point_y, endPoint,
                                                                   endPoint * k + b, dash=(2, 2), fill=color)]

            elif point_triangle(zero_point_x, zero_point_y, sb_left_x, sb_left_y, sb_right_x, sb_right_y,
                                mb_left_x, mb_left_y):

                object_coord = [[(mb_right_x + sb_left_x) / 2 - START - WIDTH/2, max_height - min(sb_center_y,
                                                                                                  mb_center_y)]]
                center_mask_obj = [(mb_right_x + sb_left_x) / 2, (mb_right_y + sb_left_y) / 2]
                k, b = eq_line(zero_point_x, zero_point_y, center_mask_obj[0], center_mask_obj[1])
                self.dict_lines[camera] = [self.canvas.create_line(zero_point_x, zero_point_y, endPoint,
                                                                   endPoint * k + b, dash=(2, 2), fill=color)]

            elif point_triangle(zero_point_x, zero_point_y, sb_left_x, sb_left_y, sb_right_x, sb_right_y,
                                mb_center_x, mb_center_y):

                object_coord = [[mb_center_x - START - WIDTH/2, max_height - min(sb_center_y, mb_center_y)]]
                self.dict_lines[camera] = [self.canvas.create_line(zero_point_x, zero_point_y, mb_center_x, mb_center_y,
                                                                   dash=(2, 2), fill=color)]
            else:
                object_coord = [[mb_center_x - START - WIDTH/2, max_height - mb_center_y],
                                [mb_center_y - START - WIDTH/2, max_height - sb_center_y]]
                self.dict_lines[camera] = [self.canvas.create_line(zero_point_x, zero_point_y, mb_center_x, mb_center_y,
                                                                   dash=(2, 2), fill=color),
                                           self.canvas.create_line(zero_point_x, zero_point_y, sb_center_x, sb_center_y,
                                                                   dash=(2, 2), fill=color)]
            return object_coord

        self.left_ray_coord = draw_raws(START, 1000, 'left')
        self.central_ray_coord = draw_raws(START + WIDTH/2, 1000, 'central')
        self.right_ray_coord = draw_raws(START + WIDTH, 1000, 'right')

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
        left_camera.data = [pixel_in_camera(x[1]/SCALE, x[0]/SCALE, -700) for x in self.left_ray_coord]
        right_camera.data = [pixel_in_camera(x[1]/SCALE, x[0]/SCALE, 700) for x in self.right_ray_coord]
        central_camera.data = [pixel_in_camera(x[1]/SCALE, x[0]/SCALE, 0) for x in self.central_ray_coord]

        D, detection_wires = bypass(left_camera, central_camera, right_camera)

        mb_center_x = (self.canvas.coords(self.canvas.moving_ball)[0] + 3 - START)
        mb_center_y = max_height - self.canvas.coords(self.canvas.moving_ball)[1] - 3
        sb_center_x = (self.canvas.coords(self.canvas.static_ball)[0] + 3 - START)
        sb_center_y = max_height - self.canvas.coords(self.canvas.static_ball)[1] - 3
        self.information_field.new_text(1.0, "Координаты зеленого объекта: H - {0}, L - {1}\n".format(mb_center_y/SCALE,
                                                                            int(abs(WIDTH/2 - mb_center_x)/SCALE)))
        self.information_field.new_text(2.0, "\nКоординаты черного объекта: H - {0}, L - {1}".format(sb_center_y/SCALE,
                                                                            int(abs(WIDTH/2 - sb_center_x)/SCALE)))
        self.information_field.new_text(3.0, "\nОбнаруженных объектов = {0}".format(detection_wires))
        self.information_field.new_text(4.0, "\nКоличество объектов левой камеры - {}".format(len(left_camera.data)))
        self.information_field.new_text(5.0, "\nКоличество объектов центральной камеры - {}".format(len(central_camera.data)))
        self.information_field.new_text(6.0, "\nКоличество объектов правой камеры - {}".format(len(right_camera.data)))
        for wire in list(range(detection_wires)):
            self.information_field.insert(7.0 + float(wire),
                                          "\nОбъект {0}: Измеренные Зигзаг - {1}; Высота - {2}".format(wire + 1,
                                                                                                       D[wire].zigzag,
                                                                                                       D[wire].h))

def main():
    root = Tk()
    ex = Example(root)
    root.geometry("700x1020")
    root.mainloop()


if __name__ == '__main__':
    main()
