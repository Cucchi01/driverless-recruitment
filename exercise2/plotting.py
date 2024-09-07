import matplotlib.pyplot as plt
import math
import numpy as np


class Plot:
    def __init__(self):
        self.fig, self.ax = plt.subplots()
        self.time_axis = []
        self.precomputed_y = []
        self.func = None

    def set_data(self, x, y=None):
        if y is None:
            if self.func is None:
                raise Exception("No function and y values provided")
            y = [self.func(time) for time in x]

        self.time_axis = x
        self.precomputed_y = y

    def plot(self):
        self.ax.plot(self.time_axis, self.precomputed_y)

    def get_fig(self):
        return self.fig

    def get_ax(self):
        return self.ax


class PlotFunction(Plot):
    def __default_function(self):
        def sin_lambda(t):
            return 5 * math.sin(2 * math.pi * 1 * t)

        return lambda t: 3 * math.pi * math.exp(-sin_lambda(t))

    def __init__(self, function=None):
        super().__init__()

        if function is None:
            function = self.__default_function()
        self.set_function(function)

    def set_function(self, func):
        self.func = func
        self.set_data()

    def set_data(self):
        x = list(np.linspace(0, 1, 100))
        super().set_data(x)
