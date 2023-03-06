# This is a sample Python script.

from scipy import interpolate
import sys
from PyQt5.QtWidgets import *


class Loads:
    def __init__(self, N=0, Mx=0, My=0, Qx=0, Qy=0, T=0, B=0):
        self.N = N
        self.Mx = Mx
        self.My = My
        self.Qx = Qx
        self.Qy = Qy
        self.T = T
        self.B = B

class SectionProperties:
    def __init__(self,
                 A=0,
                 Ix=0,
                 Iy=0,
                 Iomegan=0,
                 Sx=0,
                 Sy=0,
                 Wx=0,
                 Wy=0):
        self.A = A
        self.Ix = Ix
        self.Iy = Iy
        self.Iomegan = Iomegan
        self.Sx = Sx
        self.Sy = Sy
        self.Wx = Wx
        self.Wy = Wy

def f41(Mx, Wnmin, Ry, gamma_c):
    '''
    8.2.1 Расчет на прочность балок 1-го класса
    при действии момента в одной из главных плоскостей
    :param Mx:
    :param Wnmin:
    :param Ry:
    :param gamma_c:
    :return: check, stress
    '''
    stress = Mx / Wnmin
    check = stress / Ry / gamma_c
    return check, stress

def f42(Q, S, I, tw, Rs, gamma_c, alfa=1):
    '''
    8.2.1 Расчет на прочность балок 1-го класса
    при действии в сечении поперечной силы
    :param Q:
    :param S:
    :param I:
    :param tw:
    :param Rs:
    :param alfa:
    :param gamma_c:
    :return: check, stress
    '''
    stress = Q * S * alfa / (I * tw)
    check = stress / (Rs * gamma_c)
    return check, stress

def f43(Mx, Ixn, y, My, Iyn, x, B, omega, Iomegan, Ry, gamma_c):
    '''
    8.2.1 Расчет на прочность балок 1-го класса
    при действии моментов в двух главных плоскостях (и наличии бимомента)
    :param Mx:
    :param Ixn:
    :param y:
    :param My:
    :param Iyn:
    :param x:
    :param B:
    :param omega:
    :param Iomegan:
    :param Ry:
    :param gamma_c:
    :return: check, stress,(stressMx, stressMy, stressB)
    '''
    stressMx = Mx * y / (Ixn)
    stressMy = My * x / (Iyn)
    stressB = B * omega / (Iomegan)
    stress = stressMx + stressMy + stressB
    check = stress / (Ry * gamma_c)
    return check, stress, (stressMx, stressMy, stressB)

def f44_1(Mx, Qx, Floc, Ixn, y, Sx, lef, tw, Ry, gamma_c, alfa=1):
    '''
    8.2.1 Расчет на прочность балок 1-го класса
    при одновременном действии в стенке балки момента и поперечной силы
    :param Mx:
    :param Qx:
    :param Floc:
    :param Ixn:
    :param y:
    :param Sx:
    :param lef:
    :param tw:
    :param Ry:
    :param gamma_c:
    :return: check,stress
    '''
    sigma_x = Mx * y / Ixn
    sigma_y = f47(Floc, lef, tw)
    tau_xy = Qx * Sx * alfa / (Ixn * tw)
    stress = 0.87 * (sigma_x ** 2 - sigma_x * sigma_y + sigma_y ** 2 + 3 * tau_xy ** 2) ** 0.5
    check = stress / (Ry * gamma_c)
    return check, stress

def f44_2(Qx, Ixn, Sx, tw, Rs, gamma_c, alfa=1):
    '''
    8.2.1 Расчет на прочность балок 1-го класса
    при одновременном действии в стенке балки момента и поперечной силы
    :param Qx:
    :param Ixn:
    :param Sx:
    :param tw:
    :param Rs:
    :param gamma_c:
    :return: check,stress
    '''
    tau_xy = Qx * Sx * alfa / (Ixn * tw)
    stress = tau_xy
    check = stress / (Rs * gamma_c)
    return check, stress

def f45(s, d):
    '''
    При ослаблении стенки отверстиями для болтов левую часть формулы (42),
    а также значение  в формуле (44),следует умножать на коэффициент alfa
    :param s:
    :param d:
    :return: alfa
    '''
    alfa = s / (s - d)
    return alfa

def f46(sigma_loc, Ry, gamma_c):
    '''
    8.2.2 Расчет на прочность стенки балки,
    не укрепленной ребрами жесткости, при действии местного напряжения
    :param sigma_loc:
    :param Ry:
    :param gamma_c:
    :return: check
    '''
    check = sigma_loc / (Ry * gamma_c)
    return check

def f47(Floc, lef, tw):
    '''
    8.2.2 Расчет на прочность стенки балки,
    не укрепленной ребрами жесткости, при действии местного напряжения
    :param Floc:
    :param lef:
    :param tw:
    :return: sigma_loc
    '''
    sigma_loc = Floc / (lef * tw)
    return sigma_loc

def f48(b, h):
    '''
     lef - условная длина распределения нагрузки для случаев по рисунку 6, а) и б)
    :param b:
    :param h:
    :return:
    '''
    lef = b + 2 * h
    return lef

def f49(psi, I1f, tw):
    '''
    lef - условная длина распределения нагрузки для случаев по рисунку 6, в)
    :param psi:
    :param I1f:
    :param tw:
    :return:
    '''
    lef = psi ** 3 * (I1f / tw) ** 0.5
    return lef

def f69(Mx, Wcx, fi_b, Ry, gamma_c):
    '''
    8.4.1 Расчет на устойчивость двутавровых балок 1-го класса
    при изгибе в плоскости стенки, совпадающей с плоскостью симметрии сечения
    :param Mx:
    :param Wcx:
    :param fi_b:
    :param Ry:
    :param gamma_c:
    :return: check, stress
    '''
    stress = Mx / (fi_b * Wcx)
    check = stress / (Ry * gamma_c)
    return check, stress

def f70(Mx, Wcx, My, Wcy, B, Wc_omega, fi_b, Ry, gamma_c):
    '''
    8.4.1 Расчет на устойчивость двутавровых балок 1-го класса
    при изгибе в двух главных плоскостях (и наличии бимоментов)
    :param Mx:
    :param Wcx:
    :param My:
    :param Wcy:
    :param B:
    :param Wc_omega:
    :param fi_b:
    :param Ry:
    :param gamma_c:
    :return: check, stress,(stress1,stress2,stress3)
    '''
    stress1 = Mx / (fi_b * Wcx)
    stress2 = My / Wcy
    stress3 = B / Wc_omega
    stress = stress1 + stress2 + stress3
    check = stress / (Ry * gamma_c)
    return check, stress, (stress1, stress2, stress3)

def f71(b, t, h, Ryf=0, M=0, Wc=0, gamma_c=0):
    '''
    Условная предельная гибкость сжатого при приложении нагрузки к верхнему поясу
    :param b: ширина сжатого пояса
    :param t: толщина сжатого пояса
    :param h: расстояние между осям поясных листов
    :return: lambda_ub
    '''
    bt = b / t
    bt = 15 if bt < 15 else bt
    lambda_ub_re = 0.35 + 0.0032 * bt + (0.76 - 0.02 * bt) * b / h
    factor_stress = 1
    if Ryf != 0 & Wc != 0 & gamma_c != 0:
        sigma = M / (Wc * gamma_c)
        factor_stress = (Ryf / sigma) ** 0.5
    return lambda_ub_re * factor_stress

def f72(b, t, h, Ryf=0, M=0, Wc=0, gamma_c=0):
    '''
    Условная предельная гибкость сжатого при приложении нагрузки к нижнему поясу
    :param b: ширина сжатого пояса
    :param t: толщина сжатого пояса
    :param h: расстояние между осям поясных листов
    :return: lambda_ub
    '''
    bt = b / t
    bt = 15 if bt < 15 else bt
    lambda_ub_re = 0.57 + 0.0032 * bt + (0.92 - 0.02 * bt) * b / h
    factor_stress = 1
    if Ryf != 0 & Wc != 0 & gamma_c != 0:
        sigma = M / (Wc * gamma_c)
        factor_stress = (Ryf / sigma) ** 0.5
    return lambda_ub_re * factor_stress

def f73(b, t, h, Ryf=0, M=0, Wc=0, gamma_c=0):
    '''
    Условная предельная гибкость сжатого независимо от уровня приложения нагрузки
     при расчёте участка балки между связями или при чистом изгибе
    :param b: ширина сжатого пояса
    :param t: толщина сжатого пояса
    :param h: расстояние между осям поясных листов
    :return: lambda_ub
    '''
    bt = b / t
    bt = 15 if bt < 15 else bt
    lambda_ub_re = 0.41 + 0.0032 * bt + (0.73 - 0.016 * bt) * b / h
    factor_stress = 1
    if Ryf != 0 & Wc != 0 & gamma_c != 0:
        sigma = M / (Wc * gamma_c)
        factor_stress = (Ryf / sigma) ** 0.5
    return lambda_ub_re * factor_stress

def f_zh1(fi1):
    fi_b = fi1
    return fi_b

def f_zh2(fi1):
    fi_b = min(0.68 + 0.21 * fi1, 1)
    return fi_b

def f_zh3(Ix, Iy, hy, lef, Ry, E, psi):
    fi1 = psi * Iy / Ix * (hy / lef) ** 2 * E / Ry
    return fi1

def f_zh4(It, Iy, lef, h):
    alfa = 1.54 * It / Iy * (lef / h) ** 2
    return alfa

def f_zh5(lef, tf, h, bf, tw):
    a = 0.5 * h
    alfa = 8 * (lef * tf / (h * bf)) ** 2 * (1 + a * tw ** 3 / (bf * tf ** 3))

def f_zh6(Iy, Ix, h, h1, lef, E, Ry, psi_a):
    fi1 = psi_a * Iy / Ix * 2 * h * h1 / lef ** 2 * E / Ry
    return fi1

def f_zh7(Iy, Ix, h, h2, lef, E, Ry, psi_a):
    fi1 = psi_a * Iy / Ix * 2 * h * h2 / lef ** 2 * E / Ry
    return fi1

def f_zh8(I1, I2):
    return I1 / (I1 + I2)

def f_zh9(B, C, D):
    psi_a = (B + (B + C) ** 0.5) * D
    return psi_a

def f_zh10(n, betta):
    delta = n + 0.734* betta
    return  delta

def f_zh11(n, betta):
    mu = n + 1.145 * betta
    return mu

def f_zh12(n, b1, h):
    bh = b1/h
    betta = (2*n-1)*(0.47 - 0.035*bh*(1+bh-0.072*bh**2))
    return betta

def f_zh13(n, It, I2, lef, h):
    nu = (1-n)*(9.87*n + 0.385*It/I2*(lef/h)**2)
    return nu

def tbl_zh1(check1, check2, check3, psi1, alfa):
    psi = 0
    if check1 == 'without':
        if check2 == 'concetrated':
            if check3 == 'comp':
                if 0.1 <= alfa <= 40:
                    psi = 1.75 + 0.09 * alfa
                elif 40 < alfa <= 400:
                    psi = 3.3 + 0.053 * alfa - 4.5 * (10 ** -5) * alfa ** 2
            elif check3 == 'tens':
                if 0.1 <= alfa <= 40:
                    psi = 5.05 + 0.09 * alfa
                elif 40 < alfa <= 400:
                    psi = 6.6 + 0.053 * alfa - 4.5 * (10 ** -5) * alfa ** 2
        elif check2 == 'unifrom':
            if check3 == 'comp':
                if 0.1 <= alfa <= 40:
                    psi = 1.6 + 0.08 * alfa
                elif 40 < alfa <= 400:
                    psi = 3.15 + 0.04 * alfa - 2.7 * (10 ** -5) * alfa ** 2
            elif check3 == 'tens':
                if 0.1 <= alfa <= 40:
                    psi = 3.8 + 0.08 * alfa
                elif 40 < alfa <= 400:
                    psi = 5.35 + 0.04 * alfa - 2.7 * (10 ** -5) * alfa ** 2
    elif check1 == 'two':
        if 0.1 <= alfa <= 40:
            psi = 2.25 + 0.07 * alfa
        elif 40 < alfa <= 400:
            psi = 3.6 + 0.04 * alfa - 3.5 * (10 ** -5) * alfa ** 2
    elif check1 == 'one':
        if check2 == 'concetrated_middle':
            psi = 1.75 * psi1
        elif check2 == 'concetrated_quater':
            if check3 == 'comp':
                psi = 1.14 * psi1
            elif check3 == 'tens':
                psi = 1.6*psi1
        elif check2 == 'uniform':
            if check3 == 'comp':
                psi = 1.14 * psi1
            elif check3 == 'tens':
                psi = 1.3 * psi1

    return psi

def tbl_zh2(check1, check2, alfa):
    psi = 0
    if check1 == 'concetrated':
        if check2 == 'tens':
            if 4<=alfa<=28:
                psi = 1 + 0.16 * alfa
            elif 28 < alfa <= 100:
                psi = 4 + 0.05 * alfa
        elif check2 == 'comp':
            if 4<=alfa<=28:
                psi = 6.2 + 0.08 * alfa
            elif 28 < alfa <= 100:
                psi = 7 + 0.05 * alfa
        if check1 == 'uniform':
            psi = 1.42 * alfa ** 0.5
    return psi

def tbl_zh3(check1,fi1, fi2, n):
    fi_b = 0
    if check1 == 'comp':
        if fi2 <= 0.85:
            fi_b = min(fi1,1)
        else:
            fi_b = min(fi1 * (0.21 + 0.68*(n/fi1 + (1-n)/fi2)),1)
    elif check1 == 'tens':
        if fi2 <= 0.85:
            fi_b = fi2
        else:
            fi_b = min(0.68 + 0.21*fi2, 1)
    return fi_b

def tbl_zh4(flange, load_place, load_type, delta, mu, betta):
    B = 0
    if flange == 'comp':
        if load_place == 'tens':
            if load_type == 'concetrated_middle':
                B = delta
            elif load_type == 'uniform':
                B = mu
            else:
                B = betta
        elif load_place == 'comp':
            if load_type == 'concetrated_middle':
                B = delta - 1
            elif load_type == 'uniform':
                B = mu - 1
            else:
                B = betta
    if flange == 'tens':
        if load_place == 'tens':
            if load_type == 'concetrated_middle':
                B = 1 - delta
            elif load_type == 'uniform':
                B = 1 - mu
            else:
                B = -betta
        elif load_place == 'comp':
            if load_type == 'concetrated_middle':
                B = -delta
            elif load_type == 'uniform':
                B = -mu
            else:
                B = -betta
    return B

def tbl_zh5(load_type, section_type, n, nu, alfa):
    C, D = 0, 0
    if load_type == 'concetrated_middle':
        if section_type == 'I':
            if n <= 0.9:
                C = 0.33 * nu
        elif section_type == 'T':
            if n == 1:
                C = 0.0826 * alfa
        D = 3.265
    elif load_type == 'uniform':
        if section_type == 'I':
            if n <= 0.9:
                C = 0.481 * nu
        elif section_type == 'T':
            if n == 1:
                C = 0.1202 * alfa
        D = 2.247
    elif load_type == 'simple bending':
        if section_type == 'I':
            if n <= 0.9:
                C = 0.101 * nu
        elif section_type == 'T':
            if n == 1:
                C = 0.0253 * alfa
        D = 4.315
    return C, D




formula_dict = {41: f41}

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app = QApplication(sys.argv)
    dlgMain = QMainWindow()
    dlgMain.show()
    dlgMain.setWindowTitle('First GUI')
    app.exec()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
