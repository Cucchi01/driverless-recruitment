import time
from PyQt5.QtWidgets import (
    QVBoxLayout,
    QWidget,
    QSlider,
    QLineEdit,
    QLabel,
    QHBoxLayout,
    QPushButton,
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
)
from PyQt5.QtCore import Qt, QRunnable, QThreadPool
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from plotting import PlotFunction
import math


def __default_function(t):
    def sin_lambda(t):
        return 5 * math.sin(2 * math.pi * 1 * t)

    return 3 * math.pi * math.exp(-sin_lambda(t))


def __sin_function(t):
    return math.sin(2 * math.pi * 1 * t)


def __cos_function(t):
    return math.cos(2 * math.pi * 2 * t)


FUNCTIONS_NAMES = ["Default", "sin(2 pi x)", "cos(4 pi x)"]
EXTREMES_FUNCTIONS = [[0, 1], [0, 1], [0, 0.5]]
FUNCTIONS = [__default_function, __sin_function, __cos_function]


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        # function h(t)
        self.plot = PlotFunction()
        self.plot.plot()
        self.percentage_to_visualize = 1.0

        self.worker = None
        self.threadpool = QThreadPool()
        self.stop_worker = False
        self.reset_worker = False

        self.setWindowTitle("Driverless recruitment")
        self.__define_layout()
        self.__define_controls()

    def __define_layout(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # plot
        self.canvas = FigureCanvasQTAgg(self.plot.get_fig())
        layout.addWidget(self.canvas)

        # Options
        label_form = QLabel("Options plot:")
        layout.addWidget(label_form)

        # Change function
        layout.addWidget(QLabel("Select function"))
        self.function_combo = QComboBox()
        self.function_combo.addItems(FUNCTIONS_NAMES)
        self.function_combo.setCurrentIndex(0)
        layout.addWidget(self.function_combo)

        # Grid
        self.grid_enabled = QCheckBox("Show grid")
        self.grid_enabled.setCheckState(Qt.Checked)
        self.plot.get_ax().grid(True)
        layout.addWidget(self.grid_enabled)

        # Zoom-control on x-axis
        self.x_slider_label = QLabel("X-Axis range:")
        layout.addWidget(self.x_slider_label)
        x_zoom_layout = QHBoxLayout()
        x_zoom_layout.addWidget(QLabel("Start"))
        self.input_start_x = QDoubleSpinBox()
        self.input_start_x.setMinimum(self.__get_x_bounds()[0])
        self.input_start_x.setMaximum(self.__get_x_bounds()[1])
        self.input_start_x.setValue(self.__get_x_bounds()[0])
        self.plot.get_ax().set_xlim(left=self.__get_x_bounds()[0])
        self.input_start_x.setSingleStep(0.1)
        x_zoom_layout.addWidget(self.input_start_x)

        x_zoom_layout.addWidget(QLabel("End"))
        self.input_end_x = QDoubleSpinBox()
        self.input_end_x.setMinimum(self.__get_x_bounds()[0])
        self.input_end_x.setMaximum(self.__get_x_bounds()[1])
        self.input_end_x.setValue(self.__get_x_bounds()[1])
        self.plot.get_ax().set_xlim(right=self.__get_x_bounds()[1])
        self.input_end_x.setSingleStep(0.1)
        x_zoom_layout.addWidget(self.input_end_x)

        layout.addLayout(x_zoom_layout)

        # Buttons
        layout.addWidget(QLabel("Simulation live data"))
        buttons_layout = QHBoxLayout()
        self.start_button = QPushButton("Start")
        self.stop_button = QPushButton("Stop")
        self.reset_button = QPushButton("Reset")
        buttons_layout.addWidget(self.start_button)
        buttons_layout.addWidget(self.stop_button)
        buttons_layout.addWidget(self.reset_button)
        layout.addLayout(buttons_layout)

        # self.experiment_name_edit = QLineEdit()
        # self.experiment_name_edit.setPlaceholderText("Enter the experiment name")
        # layout.addWidget(self.experiment_name_edit)

        # self.save_button = QPushButton("Save as CSV")
        # layout.addWidget(self.save_button)

    def __reset_layout(self):
        plot_function = self.__get_function()
        self.plot.set_function(plot_function)

        self.plot.get_ax().cla()
        self.__grid_change(self.grid_enabled.checkState())
        self.plot.plot()

        min_x = self.__get_x_bounds()[0]
        max_x = self.__get_x_bounds()[1]
        self.input_start_x.setMinimum(min_x)
        self.input_start_x.setMaximum(max_x)

        self.input_end_x.setMinimum(min_x)
        self.input_end_x.setMaximum(max_x)

        self.canvas.draw()
        self.canvas.show()

    def __get_x_bounds(self):
        return EXTREMES_FUNCTIONS[self.function_combo.currentIndex()]

    def __get_function(self):
        return FUNCTIONS[self.function_combo.currentIndex()]

    def __define_controls(self):
        self.grid_enabled.stateChanged.connect(self.__grid_change)
        self.input_start_x.valueChanged.connect(self.__start_x_change)
        self.input_end_x.valueChanged.connect(self.__end_x_change)
        self.function_combo.currentIndexChanged.connect(self.__function_changed)
        self.start_button.clicked.connect(self.start_event)
        self.stop_button.clicked.connect(self.stop_event)
        self.reset_button.clicked.connect(self.reset_event)

    def __grid_change(self, s):
        if s == Qt.Checked:
            self.plot.get_ax().grid(True)
        else:
            self.plot.get_ax().grid(False)

        self.canvas.draw()

    def __start_x_change(self, i):
        self.plot.get_ax().set_xlim(left=i)
        # update the end x minimum possible value
        self.input_end_x.setMinimum(i)

        self.canvas.draw()

    def __end_x_change(self, i):
        self.plot.get_ax().set_xlim(right=i)
        self.input_start_x.setMaximum(i)

        self.canvas.draw()

    def __function_changed(self, i):  # i is an int
        self.__reset_layout()

    def get_percentage(self):
        return self.percentage_to_visualize

    def set_percentage(self, val):
        self.percentage_to_visualize = val
        bounds = self.__get_x_bounds()
        # simulate live data with update of the plot bounds
        self.input_end_x.setValue(bounds[1] * val)

    def start_event(self):
        def change_percentage():
            perc = self.get_percentage()
            if perc == 1.0:
                perc = 0.0
            while perc <= 1.0:
                self.set_percentage(perc)
                time.sleep(0.1)

                if self.__get_stop_worker():
                    self.__set_stop_worker(False)
                    break

                if self.__get_reset_worker():
                    self.__set_reset_worker(False)
                    self.set_percentage(1.0)
                    break
                perc += 0.01

        self.stop_worker = False
        self.reset_worker = False
        self.worker = Worker(fn=change_percentage)
        self.threadpool.start(self.worker)

    def stop_event(self):
        self.stop_worker = True

    def reset_event(self):
        self.reset_worker = True
        if self.threadpool.activeThreadCount() == 0:
            self.set_percentage(1.0)

    def __get_stop_worker(self):
        return self.stop_worker

    def __get_reset_worker(self):
        return self.reset_worker

    def __set_stop_worker(self, val):
        self.stop_worker = val

    def __set_reset_worker(self, val):
        self.reset_worker = val


class Worker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()

        self.fn = fn
        self.args = args
        self.kwargs = kwargs

    def run(self):
        """
        Initialise the runner function with passed args, kwargs.
        """
        self.fn(*self.args, **self.kwargs)
