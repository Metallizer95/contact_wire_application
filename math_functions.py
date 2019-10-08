from math import *


def solve_square_equal(a, b, c):
    """
    :param a: Коэффициент при x в квадрате
    :param b: Коэффициент при х
    :param c: Свободный коэффициент уравнения
    :return: Возвращает корни квадратного уравнения, либо False, если таковые отсутствуют
    """
    D = b ** 2 - 4 * a * c
    if D < 0:
        return False
    elif round(D, 2) == 0:
        return [-b / (2 * a)]
    else:
        return [(-b + sqrt(D)) / (2 * a), (-b - sqrt(D)) / (2 * a)]


def equationLine(x1, y1, x2, y2):
    """
    Нахождение уравнения прямой по двум точкам
    """
    try:
        k = (y2 - y1) / (x2 - x1)
    except ZeroDivisionError:
        k = 0
    b = y1 - k * x1
    return k, b


def check_line_in_circle(circle, kLine, bLine):
    """
    :param circle: список/кортеж, который содержит информацию о заданной окружности
    :param kLine: Коэффициент при x в уравнении прямой
    :param bLine: Свободный коэффициент в уравнении прямой
    :return: Возвращает точки пересечения заданной окружности и прямой либо False, если
    таковые отсутствуют
    """
    a = circle[0]
    b = circle[1]
    r = circle[2]
    k = kLine
    d = bLine

    x2 = 1 + k ** 2
    x = -2 * a + 2 * k * d - 2 * k * b
    c = a ** 2 + d ** 2 + b ** 2 - 2 * b * d - r ** 2
    solve = solve_square_equal(x2, x, c)
    if not solve:
        return solve
    elif len(solve) == 1:
        return solve[0], k * solve[0] + d
    else:
        y1 = solve[0] * k + d
        y2 = solve[1] * k + d
        yMin = max(y1, y2)
        xMin = (yMin - d) / k
        return xMin, yMin
