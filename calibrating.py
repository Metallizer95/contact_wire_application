"""
Калбировка представляет собой вычисление координат эквидистантных объектов на заданной высоте
"""
from main import Example, WIRE_WIDTH
import detectionAlg as detect
import canvas_class as cc
H = 5400

class Calibrating(Example):
    def __init__(self, calibrateHeight):
        Example.__init__(self)

    def initUI(self):
        # Создание 4-х проводов
        self.create_wire(-600, H, WIRE_WIDTH/2)
        self.create_wire(-300, H, WIRE_WIDTH/2)
        self.create_wire(300, H, WIRE_WIDTH/2)
        self.create_wire(600, H, WIRE_WIDTH / 2)

        # Создание 3-х камер
        self.create_camera(-700, 0, 29.184, 75, 8)
        self.create_camera(0, 0, 29.184, 75, 0)
        self.create_camera(700, 0, 29.184, 75, -8)

        self.create_graphs()

    def create_graphs(self):
        self.arrowCamera1 = self.oscilloscope(list(self.all_camera.items())[0][1])
        self.arrowCamera2 = self.oscilloscope(list(self.all_camera.items())[1][1])
        self.arrowCamera3 = self.oscilloscope(list(self.all_camera.items())[2][1])

    def getCoefficient(self):
        """Вычисление коэффициентов калибровки"""
        leftCameraObj = detect.detectAlg(self.arrowCamera1, demask=detect.demask)
        tgLeftCamera = [0.018518518518518517, 0.07407407407407407, 0.18518518518518517, 0.24074074074074073]

        centerCameraObj = detect.detectAlg(self.arrowCamera2, demask=detect.demask)
        tgCentreCamera = [0.1111111111111111, 0.05555555555555555, -0.05555555555555555, -0.1111111111111111]

        rightCameraObj = detect.detectAlg(self.arrowCamera3, demask=detect.demask)
        tgRightCamera = [0.24074074074074073, 0.18518518518518517, 0.07407407407407407, 0.018518518518518517]

        leftCoefficients = detect.cameraCalibrating(leftCameraObj, tgLeftCamera)
        centerCoefficients = detect.cameraCalibrating(centerCameraObj, tgCentreCamera)
        rightCoefficients = detect.cameraCalibrating(rightCameraObj, tgRightCamera)
        return leftCoefficients, centerCoefficients, rightCoefficients

def getCalibratingCoefficient():
    ex = Calibrating()
    left, center, right = ex.getCoefficient()
    return left, center, right

