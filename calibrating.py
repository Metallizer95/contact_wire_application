"""
Калбировка представляет собой вычисление координат эквидистантных объектов на заданной высоте
"""
import tkinter as tk
import detectionAlg as detect
import canvas_class as cc
import math_functions as mf
H = 5400
WIRE_WIDTH = 14*0.15
class Calibrating(tk.Frame):
    def __init__(self, parent=None):
        tk.Frame.__init__(self, parent)
        self.canvas = cc.Canvas_object(self)

        # Хэш таблицы всех камер и проводов
        self.all_camera = {}
        self.all_wire = {}

        # Инициализация Users Interface
        self.initUI()

    def initUI(self):
        # Создание объектов взаимодействия
        self.ball_1st = self.create_wire(-600, H, WIRE_WIDTH / 2)
        self.ball_2nd = self.create_wire(-300, H, WIRE_WIDTH / 2)
        self.ball_3rd = self.create_wire(300, H, WIRE_WIDTH / 2)
        self.ball_4th = self.create_wire(600, H, WIRE_WIDTH / 2)
        self.create_camera(-700, 0, 29.184, 75, 7.38604)
        self.create_camera(0, 0, 29.184, 75, 0)
        self.create_camera(700, 0, 29.184, 75, -7.38604)

        self.create_graphs()

    def create_graphs(self):
        self.arrowCamera1 = self.oscilloscope(list(self.all_camera.items())[0][1])
        self.arrowCamera2 = self.oscilloscope(list(self.all_camera.items())[1][1])
        self.arrowCamera3 = self.oscilloscope(list(self.all_camera.items())[2][1])

    def oscilloscope(self, camera):
        """Формирование массива данных, полученных с камеры"""
        osc = []
        if not camera.coefs:
            camera.coefs = self.canvas.move_ray(camera)
        for item in camera.coefs.keys():
            if (mf.check_line_in_circle(self.all_wire[self.ball_1st].all_data, camera.coefs[item][0], camera.coefs[item][1]) or
                    mf.check_line_in_circle(self.all_wire[self.ball_2nd].all_data, camera.coefs[item][0], camera.coefs[item][1]) or
                    mf.check_line_in_circle(self.all_wire[self.ball_3rd].all_data, camera.coefs[item][0], camera.coefs[item][1]) or
                    mf.check_line_in_circle(self.all_wire[self.ball_4th].all_data, camera.coefs[item][0], camera.coefs[item][1])):
                osc.append(1)
            else:
                osc.append(0)
        osc.reverse()
        return osc

    def create_wire(self, xCord, yCord, radius, **config):
        """Функция построения на холсте объекта провод и запись его внутренних значений в хэш таблицу"""
        wire = self.canvas.create_circle(xCord, yCord, radius, **config)
        self.all_wire[wire[0]] = wire[1]
        return wire[0]

    def create_camera(self, xCenter, yCenter, w, h, angle, **config):
        """ Функция построения на холсте объекта камера и запись характеристик в хэш таблицу"""
        l = len(self.all_camera)
        camera = self.canvas.create_camera(xCenter, yCenter, w, h, angle, **config)
        self.all_camera[l] = camera[1]

    def getCoefficient(self):
        """Вычисление коэффициентов калибровки"""
        leftCameraObj = detect.detectAlg(self.arrowCamera1, demask=detect.demask)
        tgLeftCamera = [0.018518518518518517, 0.07407407407407407, 0.18518518518518517, 0.24074074074074073]

        centerCameraObj = detect.detectAlg(self.arrowCamera2, demask=detect.demask)
        centerCameraObj.remove(1824)
        tgCentreCamera = [0.1111111111111111, 0.05555555555555555, -0.05555555555555555, -0.1111111111111111]

        rightCameraObj = detect.detectAlg(self.arrowCamera3, demask=detect.demask)
        tgRightCamera = [0.24074074074074073, 0.18518518518518517, 0.07407407407407407, 0.018518518518518517]
        print(leftCameraObj)
        print(centerCameraObj)
        print(rightCameraObj)

        leftCoefficients = detect.cameraCalibrating(leftCameraObj, tgLeftCamera)
        centerCoefficients = detect.cameraCalibrating(centerCameraObj, tgCentreCamera)
        rightCoefficients = detect.cameraCalibrating(rightCameraObj, tgRightCamera)
        return leftCoefficients, centerCoefficients, rightCoefficients

def getCalibratingCoefficient():
    ex = Calibrating()
    left, center, right = ex.getCoefficient()
    return left, center, right


if __name__ == '__main__':
    left, center, right = getCalibratingCoefficient()
    print(left)
    print(center)
    print(right)
