import numpy as np

MIN_EPS = 3
MSX_EPS = 9
H_AVR = 6200
BASE = 1400


class Camera:
    def __init__(self, *args):
        temp = [i for i in args]
        self.data = list()
        self.data_cal = temp[0:4]
        self.tg = temp[4:8]
        self.coefs = self.calibrate_camera()

    def calibrate_camera(self):
        try:
            a = np.array([[1, self.data_cal[0], self.data_cal[0] ** 2, self.data_cal[0] ** 3],
                          [1, self.data_cal[1], self.data_cal[1] ** 2, self.data_cal[1] ** 3],
                          [1, self.data_cal[2], self.data_cal[2] ** 2, self.data_cal[2] ** 3],
                          [1, self.data_cal[3], self.data_cal[3] ** 2, self.data_cal[3] ** 3]])
            b = np.array([self.tg[0], self.tg[1], self.tg[2], self.tg[3]])
        except IndexError:
            print("Неверно записаны данные. Создайте новый инстанс")
            del self
        else:
            return list(np.linalg.solve(a, b))


class Det_obj:
    def __init__(self):
        self.h = 0
        self.zigzag = 0
        self.eps = 0

    def find_h(self, cam1, cam3):
        self.h = int(BASE / (cam1 + cam3))

    def find_zigzag(self, cam1, cam3):
        self.zigzag = int(self.h * (cam1 - cam3) / 2)


def bypass(cam1, cam2, cam3):
    camera1 = list()
    camera2 = list()
    camera3 = list()
    eps = MIN_EPS

    for i in range(len(cam1.data)):
        camera1.append(
            cam1.coefs[0] + cam1.coefs[1] * cam1.data[i] + cam1.coefs[2] * cam1.data[i] ** 2 + cam1.coefs[3] *
            cam1.data[i] ** 3)
    for i in range(len(cam2.data)):
        camera2.append(
            cam2.coefs[0] + cam2.coefs[1] * cam2.data[i] + cam2.coefs[2] * cam2.data[i] ** 2 + cam2.coefs[3] *
            cam2.data[i] ** 3)
    for i in range(len(cam3.data)):
        camera3.append(
            cam3.coefs[0] + cam3.coefs[1] * cam3.data[i] + cam3.coefs[2] * cam3.data[i] ** 2 + cam3.coefs[3] *
            cam3.data[i] ** 3)

    while True:
        amount_obj = 0
        D = dict()  # Словарь классов, которые хранят информацию о проводе
        relative_eps = eps / H_AVR
        print('\n')
        for i in range(len(cam1.data)):
            for j in range(len(cam2.data)):
                for k in range(len(cam3.data)):
                    print('({0}, {1}, {2}) - {3}'.format(i, j, k, abs(camera2[j] - (camera3[k] - camera1[i]) / 2)))
                    if abs(camera2[j] - (camera3[k] - camera1[i]) / 2) <= relative_eps:
                        D[amount_obj] = Det_obj()
                        D[amount_obj].find_h(camera1[i], camera3[k])
                        D[amount_obj].find_zigzag(camera1[i], camera3[k])
                        D[amount_obj].eps = eps * H_AVR
                        amount_obj += 1
        if amount_obj >= 2 or eps == MSX_EPS:
            break
        eps += 1
    return D, amount_obj


def pixel_in_camera(H, l, x):
    """
    :param H: height of object
    :param l: zigzag of object
    :param x: distance from center to camera
    :return: number pixel of linear camera
    """
    F = 75
    h_cal = 5400
    size_pix = 0.008

    if x == 0:
        return 1800 - round((F * l / H) / size_pix)
    else:
        tg_alpha_beta = abs(h_cal / x)
        tg_alpha = abs(H / (x - l))
    tg_beta = (tg_alpha_beta - tg_alpha) / (tg_alpha_beta * tg_alpha - 1)
    num_pix = round(tg_beta * F / size_pix)
    if x < 0:
        return 1800 - num_pix
    else:
        return 1800 + num_pix


if __name__ == '__main__':
    H = 6000
    print(pixel_in_camera(6000, -7, 0))
    print(pixel_in_camera(6000, 7, 0))
