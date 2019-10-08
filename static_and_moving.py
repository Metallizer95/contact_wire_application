from tkinter import *
from camera import *
import math_functions as mf

SCALE = 0.15
WIDTH = 210  # 1400 * SCALE
START = 15
max_height = 6800 * SCALE
WIRE_WIDTH = 14 * SCALE
threshold = WIRE_WIDTH / 2


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

    def create_border(self):
        self.create_line(START, 0, START, 1000, fill='black', width=2)
        self.create_line(START + WIDTH, 0, START + WIDTH, 1000, fill='black', width=2)

    def create_circle(self, xCord, yCord, radius, **config):
        xCord = START + WIDTH / 2 + xCord * SCALE
        yCord = max_height - yCord * SCALE
        xLeft = xCord - radius
        yLeft = yCord - radius
        xRight = xCord + radius
        yRight = yCord + radius
        circle = self.create_oval(xLeft, yLeft, xRight, yRight, **config)
        return circle, [xCord, yCord, radius]

    def draw_camera(self, xCenter, yCenter, h, w, **config):
        yCenter = max_height - yCenter * SCALE
        xCenter = START + WIDTH / 2 + xCenter * SCALE
        xLeft = xCenter - SCALE*w/2
        yLeft = yCenter - h*SCALE
        xRight = xCenter + SCALE*w/2
        yRight = yCenter
        rectangle = self.create_rectangle(xLeft, yLeft, xRight, yRight, **config)
        return rectangle, [xCenter, yLeft]


class Example(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent
        self.canvas = Canvas_ball(self)
        self.information_field = Text_tk(self)
        # Структуры для хранения данных о камерах и объектах
        self.all_circle = dict()
        self.all_camera = dict()
        self.initUI()


    def initUI(self):
        self.pack(expand=1, fill=BOTH)
        self.canvas.pack(side=LEFT, expand=1, fill=Y)
        self.information_field.pack(side=RIGHT, expand=1, fill=BOTH)
        moving_ball = self.create_ball(-600, 6000, WIRE_WIDTH / 2, fill='red')
        static_ball = self.create_ball(0, 6600, WIRE_WIDTH / 2, fill='green')
        self.create_camera(-700, 0, 75, 30)
        self.create_camera(0, 0, 75, 30)
        self.create_camera(700, 0, 75, 30)

        # Binding buttons
        self.canvas.focus_set()
        self.canvas.bind('<Left>', lambda event: self.move_left(moving_ball))
        self.canvas.bind('<Right>', lambda event: self.move_right(moving_ball))
        self.canvas.bind('<Up>', lambda event: self.move_up(moving_ball))
        self.canvas.bind('<Down>', lambda event: self.move_down(moving_ball))
        self.canvas.bind('a', lambda event: self.move_left(static_ball))
        self.canvas.bind('d', lambda event: self.move_right(static_ball))
        self.canvas.bind('w', lambda event: self.move_up(static_ball))
        self.canvas.bind('s', lambda event: self.move_down(static_ball))

    def move_right(self, ball):
        if self.canvas.coords(ball)[2] <= START + WIDTH:
            self.canvas.move(ball, 0.75, 0)

    def move_left(self, ball):
        if self.canvas.coords(ball)[0] >= 15:
            self.canvas.move(ball, -0.75, 0)

    def move_up(self, ball):
        if self.canvas.coords(ball)[1] >= 0:
            self.canvas.move(ball, 0, -0.75)

    def move_down(self, ball):
        if self.canvas.coords(ball)[3] <= max_height - 5400 * SCALE:
            self.canvas.move(ball, 0, 0.75)

    def cameraVision(self):
        self.objects = dict()
        for camera in self.all_camera:
            count_width = 0
            zero_x = self.all_camera[camera][0]
            zero_y = self.all_camera[camera][1]
            yRay = zero_y - 500
            xRayLeft = zero_y - 500 * 1.73205
            xRayRight = zero_y + 500 * 1.73205
            solve = set()
            while xRayLeft <= xRayRight:
                k, b = mf.equationLine(zero_x, zero_y, xRayLeft, yRay)
                if k == 0:
                    xRayLeft += 0.0001
                    continue
                m = list()
                for key in self.all_circle:
                    m.append(mf.check_line_in_circle(self.all_circle[key], k, b))
                if m[0] is False and m[1] is False:
                    if not (camera in self.objects.keys()):
                        self.objects[camera] = list()
                    solve = solve - {False}
                    self.objects[camera].append()
                    count_width = 0
                else:
                    solve.add(m[0])
                    solve.add(m[1])
                    count_width += 1

    def change_data(self):
        """
        Функция, вычисляющая параметры контактного провода;
        Все значения вывод в текст-бокс UI
        Калибровочные данные для высоты 5400 мм

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

        mb_center_x = (self.canvas.coords(self.canvas.moving_ball)[0] + WIRE_WIDTH/2 - START)
        mb_center_y = max_height - self.canvas.coords(self.canvas.moving_ball)[1] - WIRE_WIDTH/2
        sb_center_x = (self.canvas.coords(self.canvas.static_ball)[0] + WIRE_WIDTH/2 - START)
        sb_center_y = max_height - self.canvas.coords(self.canvas.static_ball)[1] - WIRE_WIDTH/2
        self.information_field.new_text(1.0, "Координаты зеленого объекта: H - {0}, L - {1}".format(mb_center_y/SCALE,
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
        """

    def create_ball(self, xCord, yCord, radius, **config):
        ball = self.canvas.create_circle(xCord, yCord, radius, **config)
        self.all_circle[ball[0]] = ball[1]
        return ball[0]

    def create_camera(self, xCenter, yCenter, h, w, **config):
        camera = self.canvas.draw_camera(xCenter, yCenter, h, w, **config)
        self.all_camera[camera[0]] = camera[1]
        return camera[0]


def main():
    root = Tk()
    ex = Example(root)
    root.geometry("700x1020")
    root.mainloop()


if __name__ == '__main__':
    main()
