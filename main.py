from tkinter import *
from canvas_class import *
from calibrating import getCalibratingCoefficient
import matplotlib.pyplot as plt
import detectionAlg
WIRE_WIDTH = 14
DEMASK = True

class Text_tk(Text):
    def __init__(self, parent=None, **config):
        Text.__init__(self, parent, **config)

    def new_text(self, row, text):
        self.delete(row, END)
        self.insert(row, text)
        return row


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
        self.create_camera(-700, 0, 29.184, 75, 7.38604)
        self.create_camera(0, 0, 29.184, 75, 0)
        self.create_camera(700, 0, 29.184, 75, -7.38604)

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

        self.create_graphs()
        self.getInformation()
        self.show_information_regarding_wire()

    def create_graphs(self):
        self.res1 = self.oscilloscope(list(self.all_camera.items())[0][1])
        self.res2 = self.oscilloscope(list(self.all_camera.items())[1][1])
        if self.res2[1823] and (not self.res2[1822] and not self.res2[1824]):
            self.res2[1823] = 0
        self.res3 = self.oscilloscope(list(self.all_camera.items())[2][1])
        x = list(range(0, 3648, 1))
        plt.gcf()
        self.ax1.clear()
        self.ax2.clear()
        self.ax3.clear()
        self.ax1.plot(x, self.res1)
        self.ax2.plot(x, self.res2)
        self.ax3.plot(x, self.res3)
        plt.draw()
        plt.show()

    def move_right(self, ball):
        if self.canvas.coords(ball)[2] <= START + WIDTH:
            self.move_wire(ball, 5, 0)
            self.create_graphs()
            self.getInformation()
            self.show_information_regarding_wire()

    def move_left(self, ball):
        if self.canvas.coords(ball)[0] >= 15:
            self.move_wire(ball, -5, 0)
            self.create_graphs()
            self.getInformation()
            self.show_information_regarding_wire()

    def move_up(self, ball):
        if self.canvas.coords(ball)[1] >= 0:
            self.move_wire(ball, 0, 5)
            self.create_graphs()
            self.getInformation()
            self.show_information_regarding_wire()

    def move_down(self, ball):
        if self.canvas.coords(ball)[3] <= MAX_H - 5400 * SCALE:
            self.move_wire(ball, 0, -5)
            self.create_graphs()
            self.getInformation()
            self.show_information_regarding_wire()

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

    def show_information_regarding_wire(self):
        row = self.information_field.new_text(1.0, "\nДемаскирование отсутствует")
        for i in range(self.amountWires):
            row = self.information_field.new_text(row + 1, "\nОбъект {0}".format(i + 1))
            row = self.information_field.new_text(row + 1, "\n{}".format(self.detectedWires[i].h))
            row = self.information_field.new_text(row + 1, "\n{}".format(self.detectedWires[i].zigzag))
            row = self.information_field.new_text(row + 1, "\n{}".format(self.detectedWires[i].eps))

    def getInformation(self):
        leftCalCoefs, centerCalCoefs, rightCalCoefs = getCalibratingCoefficient()
        leftCamera = detectionAlg.Camera(leftCalCoefs)
        centerCamera = detectionAlg.Camera(centerCalCoefs)
        rightCamera = detectionAlg.Camera(rightCalCoefs)
        leftCamera.data = detectionAlg.detectAlg(self.res1, demask=DEMASK)
        centerCamera.data = detectionAlg.detectAlg(self.res2, demask=DEMASK)
        rightCamera.data = detectionAlg.detectAlg(self.res3, demask=DEMASK)
        self.detectedWires, self.amountWires = detectionAlg.bypass(leftCamera, centerCamera, rightCamera)

    def create_wire(self, xCord, yCord, radius, **config):
        """Функция построения на холсте объекта провод и запись его параметров в хэш таблицу"""
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


def main():
    root = Tk()
    ex = Example(root)
    root.geometry("700x1020")
    root.mainloop()


if __name__ == '__main__':
    main()
