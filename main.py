from tkinter import *
from camera import *
from canvas_class import *
import matplotlib.pyplot as plt

WIRE_WIDTH = 14


class Text_tk(Text):
    def __init__(self, parent=None, **config):
        Text.__init__(self, parent, **config)

    def new_text(self, row, text):
        self.delete(row, END)
        self.insert(row, text)


class Example(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent
        self.canvas = Canvas_object(self, height=1020, width=240)
        self.information_field = Text_tk(self)

        # Создание поля для рисования графиков
        plt.interactive(True)
        self.fig, (self.ax1, self.ax2, self.ax3) = plt.subplots(3, 1)

        # Хэш таблицы всех камер и проводов
        self.all_camera = {}
        self.all_wire = {}

        # Инициализация Users Interface
        self.initUI()

    def initUI(self):
        # Размещение объектов на GUI
        self.pack(expand=1, fill=BOTH)
        self.canvas.pack(side=LEFT, expand=1, fill=Y)
        self.information_field.pack(side=RIGHT, expand=1, fill=BOTH)

        # Создание объектов взаимодействия
        self.moving_ball = self.create_wire(-600, 6000, WIRE_WIDTH / 2, fill='red')
        self.static_ball = self.create_wire(0, 6600, WIRE_WIDTH / 2, fill='green')
        self.create_camera(-700, 0, 29.184, 75, 8)
        self.create_camera(0, 0, 29.184, 75, 0)
        self.create_camera(700, 0, 29.184, 75, -8)

        # Биндинг кнопок передвижения шариков
        self.canvas.focus_set()
        self.canvas.bind('<Left>', lambda event: self.move_left(self.moving_ball))
        self.canvas.bind('<Right>', lambda event: self.move_right(self.moving_ball))
        self.canvas.bind('<Up>', lambda event: self.move_up(self.moving_ball))
        self.canvas.bind('<Down>', lambda event: self.move_down(self.moving_ball))
        self.canvas.bind('a', lambda event: self.move_left(self.static_ball))
        self.canvas.bind('d', lambda event: self.move_right(self.static_ball))
        self.canvas.bind('w', lambda event: self.move_up(self.static_ball))
        self.canvas.bind('s', lambda event: self.move_down(self.static_ball))

        self.cameraBorder()
        self.create_graphs()

    def create_graphs(self):
        res1 = self.oscilloscope(list(self.all_camera.items())[0][1])
        res2 = self.oscilloscope(list(self.all_camera.items())[1][1])
        res3 = self.oscilloscope(list(self.all_camera.items())[2][1])
        x = list(range(0, 3648, 1))
        plt.gcf()
        self.ax1.clear()
        self.ax2.clear()
        self.ax3.clear()
        self.ax1.plot(x, res1)
        self.ax2.plot(x, res2)
        self.ax3.plot(x, res3)
        plt.draw()
        plt.show()

    def move_right(self, ball):
        if self.canvas.coords(ball)[2] <= START + WIDTH:
            self.move_wire(ball, 5, 0)
            self.create_graphs()

    def move_left(self, ball):
        if self.canvas.coords(ball)[0] >= 15:
            self.move_wire(ball, -5, 0)
            self.create_graphs()

    def move_up(self, ball):
        if self.canvas.coords(ball)[1] >= 0:
            self.move_wire(ball, 0, 5)
            self.create_graphs()

    def move_down(self, ball):
        if self.canvas.coords(ball)[3] <= MAX_H - 5400 * SCALE:
            self.move_wire(ball, 0, -5)
            self.create_graphs()

    def oscilloscope(self, camera):
        """Формирование массива данных, полученных с камеры"""
        osc = []
        if not camera.coefs:
            camera.coefs = self.canvas.move_ray(camera)
        for item in camera.coefs.keys():
            if (mf.check_line_in_circle(self.all_wire[self.moving_ball].all_data, camera.coefs[item][0], camera.coefs[item][1]) or
                    mf.check_line_in_circle(self.all_wire[self.static_ball].all_data, camera.coefs[item][0], camera.coefs[item][1])):
                osc.append(1)
            else:
                osc.append(0)
        osc.reverse()
        return osc

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

    def create_wire(self, xCord, yCord, radius, **config):
        """Функция построения на холсте объекта провод и запись его внутренних значений в хэш таблицу"""
        wire = self.canvas.create_circle(xCord, yCord, radius, **config)
        self.all_wire[wire[0]] = wire[1]
        return wire[0]

    def move_wire(self, wire, x, y):
        """Передвигает провод на холсте и переписывает его координаты"""
        x = x*SCALE
        y = y*SCALE
        self.canvas.move(wire, x, -y)
        xCenter = self.canvas.coords(wire)[0] + SCALE*WIRE_WIDTH/2
        yCenter = self.canvas.coords(wire)[1] + SCALE * WIRE_WIDTH / 2
        self.all_wire[wire].change_data(xCenter, yCenter)

    def create_camera(self, xCenter, yCenter, w, h, angle, **config):
        """ Функция построения на холсте объекта камера и запись характеристик в хэш таблицу"""
        l = len(self.all_camera)
        camera = self.canvas.create_camera(xCenter, yCenter, w, h, angle, **config)
        self.all_camera[l] = camera[1]

    def cameraBorder(self):
        """Показать границы видимости камер"""
        self.canvas.create_line(self.all_camera[0].zero_x, self.all_camera[0].zero_y,
                                self.all_camera[0].xLeftRay, self.all_camera[0].yLeftRay, fill='red')
        self.canvas.create_line(self.all_camera[0].zero_x, self.all_camera[0].zero_y,
                                self.all_camera[0].xRightRay, self.all_camera[0].yRightRay, fill='red')

        self.canvas.create_line(self.all_camera[1].zero_x, self.all_camera[1].zero_y,
                                self.all_camera[1].xLeftRay, self.all_camera[1].yLeftRay, fill='red')
        self.canvas.create_line(self.all_camera[1].zero_x, self.all_camera[1].zero_y,
                                self.all_camera[1].xRightRay, self.all_camera[1].yRightRay, fill='red')

        self.canvas.create_line(self.all_camera[2].zero_x, self.all_camera[2].zero_y,
                                self.all_camera[2].xLeftRay, self.all_camera[2].yLeftRay, fill='red')
        self.canvas.create_line(self.all_camera[2].zero_x, self.all_camera[2].zero_y,
                                self.all_camera[2].xRightRay, self.all_camera[2].yRightRay, fill='red')


def main():
    root = Tk()
    ex = Example(root)
    root.geometry("700x1020")
    root.mainloop()


if __name__ == '__main__':
    main()
