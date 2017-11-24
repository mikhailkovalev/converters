from api import sign
from converters import *

class IConverterDecorator(IConverter):
    def __init__(self, stuffing):
        self.stuffing = stuffing

    def convert(self, arg):
        return self.stuffing.convert(arg)

    def get_stuffing(self):
        return stuffing

class RectangleConverterDecorator(IConverterDecorator, RectangleConverter):
    def __init__(self, stuffing):
        super().__init__(stuffing)

    def get_scale_x(self):
        return self.stuffing.get_scale_x()

    def set_scale_x(self, value):
        self.stuffing.set_scale_x(value)

    def get_scale_y(self):
        return self.stuffing.get_scale_y()

    def set_scale_y(self, value):
        self.stuffing.set_scale_y(value)

    def get_translate_x(self):
        return self.stuffing.get_translate_x()

    def set_translate_x(self, value):
        self.stuffing.set_translate_x(value)

    def get_translate_y(self):
        return self.stuffing.get_translate_y()

    def set_translate_y(self, value):
        self.stuffing.set_translate_y(value)

    def _set_matrix(self):
        return self.stuffing._set_matrix()

    def get_matrix(self):
        return self.stuffing.get_matrix()

    def reconfig(self, args, values):
        return self.stuffing.reconfig(args, values)


class ToScreenDecorator(RectangleConverterDecorator):
    @staticmethod
    def round(x):
        """
        Функция округления. Нужна, чтобы возвращаемым
        значением был int
        """
        return int(0.5 + x)

    def convert(self, arg):
        """
        Вызывает метод родителя и округляет
        полученный результат до ближайших целых
        """
        value = super().convert(arg)
        return list(map(self.round, value))


class UndeformatingDecorator(RectangleConverterDecorator):
    """
    Коэффициенты растяжения вдоль обеих осей одинаковы
    """
    def __init__(self, stuffing, inside=True):
        """
        Параметр inside говорит о том, должна ли область аргументов
        целиком поместиться внутри области значений
        """
        super().__init__(stuffing)
        self.extr = self.min if inside else self.max

    def max(self, *args):
        return max(*args)

    def min(self, *args):
        return min(*args)


    def reconfig(self, args, values):
        arg_left, arg_top = args[0]
        arg_right, arg_bottom = args[1]

        value_left, value_top = values[0]
        value_right, value_bottom = values[1]

        delta_arg_x = arg_right - arg_left
        delta_arg_y = arg_bottom - arg_top

        delta_value_x = value_right - value_left
        delta_value_y = value_bottom - value_top

        s1x = sign(delta_arg_x)
        s1y = sign(delta_arg_y)

        t1x = -arg_left * s1x
        t1y = -arg_top * s1y

        s3x = sign(delta_value_x)
        s3y = sign(delta_value_y)

        delta_value_x = abs(delta_value_x)
        delta_value_y = abs(delta_value_y)
        delta_arg_x = abs(delta_arg_x)
        delta_arg_y = abs(delta_arg_y)

        s2 = self.extr(delta_value_x/delta_arg_x, delta_value_y/delta_arg_y)

        t2x = 0.5*(delta_value_x - s2*delta_arg_x)
        t2y = 0.5*(delta_value_y - s2*delta_arg_y)

        mtx = 'M{0}:\n{1:.2f}  0.00  {2:.2f}\n0.00  {3:.2f}  {4:.2f}\n'

        print(mtx.format(1, s1x, t1x, s1y, t1y))
        print(mtx.format(2, s2, t2x, s2, t2y))
        print(mtx.format(3, s3x, value_left, s3y, value_top))


        self.set_scale_x(s3x * s2 * s1x)
        self.set_scale_y(s3y * s2 * s1y)

        self.set_translate_x(value_left + s3x*(t2x + s2*t1x))
        self.set_translate_y(value_top + s3y*(t2y + s2*t1y))

        self._set_matrix()
        print(self.get_matrix())
        # # TODO: Добавить проверку деления на ноль?
        # self.stuffing.scale_x = (value_right-value_left) / (arg_right-arg_left)
        # self.stuffing.scale_y = (value_bottom-value_top) / (arg_bottom-arg_top)
        #
        # # FIXME: Сейчас считает правильно только для положительных масштабов!
        # # FIXME: Масштабы должны быть одинаковы по модулю,
        # # FIXME: но сохранять свой знак!
        # scale = min(map(abs, (self.stuffing.scale_x, self.stuffing.scale_y)))
        # print('scale_x = {0}\nscale_y = {1}\nscale   = {2}\n\n'.format(
        # self.stuffing.scale_x, self.stuffing.scale_y, scale
        # ))
        # self.stuffing.scale_x = math.copysign(scale, self.stuffing.scale_x)
        # self.stuffing.scale_y = math.copysign(scale, self.stuffing.scale_y)
        #
        #
        # arg_horizontal_center = 0.5 * (arg_left + arg_right)
        # arg_vertical_center = 0.5 * (arg_top + arg_bottom)
        #
        # value_horizontal_center = 0.5 * (value_left + value_right)
        # value_vertical_center = 0.5 * (value_top + value_bottom)
        #
        # self.stuffing.translate_x = value_horizontal_center - self.stuffing.scale_x*arg_horizontal_center
        # self.stuffing.translate_y = value_vertical_center - self.stuffing.scale_y*arg_vertical_center
        #
        # self.stuffing.matrix = self.get_matrix()
