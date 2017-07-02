import numpy as np

class IConverter:
    def convert(self, arg):
        """
        Находит образ точки arg из отображаемой области
        в области значений

        Args:
            arg -- точка из отображаемой области

        Returns:
            точка области значений, соответствующая
            аргументу
        """
        pass


class SegmentConverter(IConverter):
    def __init__(self):
        """
        Переводит линейно один отрезок
        на другой отрезок
        """
        self._scale = 1.0
        self._translate = 0.0

    def get_scale(self):
        return self._scale

    def set_scale(self, value):
        self._scale = value

    def get_translate(self):
        return self._translate

    def set_translate(self, value):
        self._translate = value

    def convert(self, arg):
        return self._scale * arg + self._translate

    def reconfig(self, args, values):
        """
        Пересчитывает коэффициенты преобразований
        в соответствии с аргументами:

        Args:
            args -- задаёт отображаемый отрезок в виде
            (left, right)

            values -- задаёт отрезок значений в виде
            (left, right)

            Не обязательно выполнение условия
            left < right
            для обоих аргументов
        """
        arg_left, arg_right = args
        value_left, value_right = values

        self._scale = (value_right-value_left) / (arg_right - arg_left)
        self._translate = value_left - self._scale*arg_left


class RectangleConverter(IConverter):
    def __init__(self):
        """
        Задаёт идентичное преобразование
        """
        self._scale_x = 1.0
        self._scale_y = 1.0

        self._translate_x = 0.0
        self._translate_y = 0.0

        self._set_matrix()

    def get_scale_x(self):
        return self._scale_x

    def set_scale_x(self, value):
        self._scale_x = value

    def get_scale_y(self):
        return self._scale_y

    def set_scale_y(self, value):
        self._scale_y = value

    def get_translate_x(self):
        return self._translate_x

    def set_translate_x(self, value):
        self._translate_x = value

    def get_translate_y(self):
        return self._translate_y

    def set_translate_y(self, value):
        self._translate_y = value

    def _set_matrix(self):
        self._matrix = self.get_matrix()

    def get_matrix(self):
        return np.array((
            (self._scale_x, 0.0, self._translate_x),
            (0.0, self._scale_y, self._translate_y),
            (0.0, 0.0, 1.0),
        ), dtype=np.float64)

    def convert(self, arg):
        homogenous = np.ones(3)
        homogenous[:2] = arg
        value = np.dot(self._matrix, homogenous)
        return list(value[:2])

    def reconfig(self, args, values):
        """
        Пересчитывает коэффициенты преобразований
        в соответствии с аргументами

        Args:
            args -- задаёт прямоугольник отображаемой
            области в виде
            ((left, top), (right, bottom))

            values -- задаёт прямоугольник в области
            значений
            ((left, top), (right, bottom))

            На деле не обязательно, чтобы выполнялось
            left < right и top < bottom
        """
        arg_left, arg_top = args[0]
        arg_right, arg_bottom = args[1]

        value_left, value_top = values[0]
        value_right, value_bottom = values[1]

        # TODO: Добавить проверку деления на ноль?
        self._scale_x = (value_right-value_left) / (arg_right-arg_left)
        self._scale_y = (value_bottom-value_top) / (arg_bottom-arg_top)

        self._translate_x = value_left - self._scale_x*arg_left
        self._translate_y = value_top - self._scale_y*arg_top

        self._matrix = self.get_matrix()

    @classmethod
    def get_configured(cls, args, values):
        """
        Получает сконфигурированный объект класса.
        Равносилен созданию объекта, и вызову у
        него метода reconfig
        """
        converter = cls()
        converter.reconfig(args, values)
        return converter


# class UndeformatingRectangleConverter(RectangleConverter):
#     """
#     Коэффициенты растяжения вдоль обеих осей одинаковы
#     """
#     def reconfig(self, args, values):
#         # Бля*ская копипаста, но что поделаешь?
#         arg_left, arg_top = args[0]
#         arg_right, arg_bottom = args[1]
#
#         value_left, value_top = values[0]
#         value_right, value_bottom = values[1]
#
#         # TODO: Добавить проверку деления на ноль?
#         self._scale_x = (value_right-value_left) / (arg_right-arg_left)
#         self._scale_y = (value_bottom-value_top) / (arg_bottom-arg_top)
#
#         scale = min(self._scale_x, self._scale_y)
#
#         arg_horizontal_center = 0.5 * (arg_left + arg_right)
#         arg_vertical_center = 0.5 * (arg_top + arg_bottom)
#
#         value_horizontal_center = 0.5 * (value_left + value_right)
#         value_vertical_center = 0.5 * (value_top + value_bottom)
#
#         self._translate_x = value_horizontal_center - scale*arg_horizontal_center
#         self._translate_y = value_vertical_center - scale*arg_vertical_center
#         self._scale_x = self._scale_y = scale
#
#         self._matrix = self.get_matrix()


# class LinearConverter:
#     def __init__(self, args, values):
#         if len(args) != 2 or len(values) != 2:
#             raise Exception('Не могу построить однозначное преобразование')
#         if not all_same(map(len, args)):
#             raise Exception('Не совпадают размерности аргументов')
