import numpy as np

# Defines
MIN_EPS = 3
MAX_EPS = 9
AVERAGE_H = 6200
BASE = 1400
demask = False

class DetectionObject:
    """Класс для храннения информации об обнаруженных объектах"""
    def __init__(self):
        self.h = 0
        self.zigzag = 0
        self.eps = 0

    def find_height(self, cam1, cam3):
        self.h = int(BASE/(cam1 + cam3))

    def find_zigzag(self, cam1, cam3):
        self.zigzag = int(self.h * (cam1 - cam3)/2)

class Camera:
    """Класс, обеспечивающий хранение данных и калибровку камер"""
    def __init__(self, coefs):
        self.coefs = coefs
        self.data = []


def detectAlg(detectionVector, demask=demask):
    """Алгоритм обнаружения с линейки. По массиву данных формирует массив центров обнаруженных объектов."""
    centerObjects = []
    count = 0
    LenHalfObj = 12
    for k, sample in enumerate(detectionVector):
        if sample:
            count += 1
        elif not sample and count:
            if count <= 25:
                centerObjects.append(k - int(count/2))
            elif count > 25 and demask:
                centerObjects.append(int(k - LenHalfObj))
                centerObjects.append(int(k - count + LenHalfObj))
            else:
                # Если объект превышает значение 25 пикселов, а нет режима демаскирования, то объект пропускается
                pass
            count = 0
    centerObjects.reverse()
    return centerObjects

def cameraCalibrating(valuePixelCal, tgDataCal):
    """Нахождение коэффициентов калибровки"""
    try:
        a = np.array([[1, valuePixelCal[0], valuePixelCal[0] ** 2, valuePixelCal[0] ** 3],
                      [1, valuePixelCal[1], valuePixelCal[1] ** 2, valuePixelCal[1] ** 3],
                      [1, valuePixelCal[2], valuePixelCal[2] ** 2, valuePixelCal[2] ** 3],
                      [1, valuePixelCal[3], valuePixelCal[3] ** 2, valuePixelCal[3] ** 3]])
        b = np.array([tgDataCal[0], tgDataCal[1], tgDataCal[2], tgDataCal[3]])
    except IndexError:
        pass
    else:
        return list(np.linalg.solve(a, b))

def bypass(cam1, cam2, cam3):
    camera1, camera2, camera3 = [], [], []
    maxWireCamera1, maxWireCamera2, maxWireCamera3 = 0, 0, 0
    eps = MIN_EPS  # Задаёт окрестность вокруг центра объекта, в которой производится поиск совпадений

    for i in range(len(cam1.data)):
        camera1.append(
            cam1.coefs[0] + cam1.coefs[1] * cam1.data[i] + cam1.coefs[2] * cam1.data[i] ** 2 + cam1.coefs[3] *
            cam1.data[i] ** 3)
        maxWireCamera1 = i

    for i in range(len(cam2.data)):
        camera2.append(
            cam2.coefs[0] + cam2.coefs[1] * cam2.data[i] + cam2.coefs[2] * cam2.data[i] ** 2 + cam2.coefs[3] *
            cam2.data[i] ** 3)
        maxWireCamera2 = i

    for i in range(len(cam3.data)):
        camera3.append(
            cam3.coefs[0] + cam3.coefs[1] * cam3.data[i] + cam3.coefs[2] * cam3.data[i] ** 2 + cam3.coefs[3] *
            cam3.data[i] ** 3)
        maxWireCamera3 = i

    maxAmountWires = max(maxWireCamera1, maxWireCamera2, maxWireCamera3)
    while True:
        amountObj = 0
        d = {}  # Словарь классов, которые хранят информацию о проводе
        relEps = eps/AVERAGE_H
        for i in range(len(cam1.data)):
            for j in range(len(cam2.data)):
                for k in range(len(cam3.data)):
                    if abs(camera2[j] - (camera3[k] - camera1[i])/2) <= relEps:
                        d[amountObj] = DetectionObject()
                        d[amountObj].find_height(camera1[i], camera3[k])
                        d[amountObj].find_zigzag(camera1[i], camera3[k])
                        d[amountObj].eps = eps*AVERAGE_H
                        amountObj += 1
        if amountObj >= maxAmountWires or eps == MAX_EPS:
            break
        eps += 1
    return d, amountObj

