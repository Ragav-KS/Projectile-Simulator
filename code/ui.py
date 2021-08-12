import os

import matplotlib as mpl
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NaviBar
from matplotlib.figure import Figure
from PyQt5 import QtCore, QtWidgets, uic

mpl.use('Qt5Agg')


class MplCanvas(FigCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        super(MplCanvas, self).__init__(self.fig)


class Ui(QtWidgets.QMainWindow):

    Pause = QtCore.pyqtSignal()
    Run = QtCore.pyqtSignal()
    Redraw = QtCore.pyqtSignal()

    blit_start = QtCore.pyqtSignal()
    blit_stop = QtCore.pyqtSignal()
    update = QtCore.pyqtSignal(float)

    def __init__(self):
        super(Ui, self).__init__()

        __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        uic.loadUi(os.path.join(__location__, '.\main.ui'), self)

        #yapf: disable
        self.lbl_Speed              : QtWidgets.QLabel
        self.lbl_Time               : QtWidgets.QLabel
        self.lbl_MaxTime            : QtWidgets.QLabel

        self.txt_dt                 : QtWidgets.QDoubleSpinBox
        self.txt_A                  : QtWidgets.QDoubleSpinBox
        self.txt_B                  : QtWidgets.QDoubleSpinBox

        self.button_Run             : QtWidgets.QPushButton
        self.button_AddProjectile   : QtWidgets.QPushButton
        self.button_Redraw          : QtWidgets.QPushButton

        self.slider_Seek            : QtWidgets.QSlider
        self.slider_Speed           : QtWidgets.QSlider

        self.PBoxContainer          : QtWidgets.QWidget
        #yapf: enable

        self.t: float = 0
        self.dt: float = self.txt_dt.value()
        self.max_t: float = 1
        self.speed: float = 1

        self.timer = QtCore.QTimer()
        self.timer.setTimerType(QtCore.Qt.PreciseTimer)
        self.timer.setInterval(1)
        self.timer.timeout.connect(self.Handler_Timer)

        self.slider_Seek.setMaximum(round(self.max_t * 1e6))
        self.slider_Seek.sliderPressed.connect(self.Handler_Slider_Seek_Press)
        self.slider_Seek.sliderReleased.connect(self.Handler_Slider_Seek_Released)
        self.slider_Seek.valueChanged.connect(self.Handler_Slider_Seek_Moved)

        self.slider_Speed.valueChanged.connect(self.Handler_Slider_Speed_Moved)

        self.canvas = MplCanvas(self)
        self.Canvas_Layout.addWidget(self.canvas)
        self.addToolBar(QtCore.Qt.TopToolBarArea, NaviBar(self.canvas, self))

        self.PBoxLayout = self.PBoxContainer.layout()

        self.__PBoxCounter = 0

        self.ProjectileBoxes = {}

        self.button_AddProjectile.clicked.connect(self.Handler_Button_AddProjectileBox_Clicked)
        self.button_Run.toggled.connect(self.Handler_Button_Run_Toggled)
        self.button_Redraw.clicked.connect(self.Handler_Button_Redraw_Clicked)

        self.Handler_Button_AddProjectileBox_Clicked()

    def Handler_Slider_Seek_Press(self):
        self.blit_start.emit()
        self.update.emit(self.t)
        pass

    def Handler_Slider_Seek_Released(self):
        self.blit_stop.emit()
        pass

    def Handler_Slider_Seek_Moved(self, val: int):
        self.t = val * 1e-6
        self.lbl_Time.setText(
            '<html><head/><body><p><span style=" font-size:10pt;">{:.2f} s</span></p></body></html>'.format(self.t, 2))
        self.update.emit(self.t)

    def Handler_Slider_Speed_Moved(self, val: int):
        self.speed = 10**(val / 100)
        self.lbl_Speed.setText(
            '<html><head/><body><p><span style=" font-size:10pt;">{:.2f}x</span></p></body></html>'.format(
                self.speed, 2))

    def Handler_Timer(self):
        self.slider_Seek.setValue((self.t + self.speed * self.dt) * 1e6)

        if self.t >= self.max_t:
            self.button_Run.setChecked(False)
        pass

    def Handler_ProjectileBoxDeleted(self, id: int):
        del self.ProjectileBoxes[id]

    def Handler_Button_AddProjectileBox_Clicked(self):
        Projbox = ProjectileBox(id=self.__PBoxCounter)

        Projbox.deleted.connect(self.Handler_ProjectileBoxDeleted)

        self.ProjectileBoxes[self.__PBoxCounter] = Projbox
        self.PBoxLayout.addWidget(Projbox)

        self.__PBoxCounter += 1

    def Handler_Button_Run_Toggled(self, checked: bool):
        if checked == True:
            self.button_Run.setToolTip('Pause')
            self.blit_start.emit()
            self.timer.start()
            self.Run.emit()
        else:
            self.button_Run.setToolTip('Run')
            self.timer.stop()
            self.blit_stop.emit()
            self.Pause.emit()

    def Handler_Button_Redraw_Clicked(self):
        self.button_Run.setChecked(False)
        self.t = 0
        self.slider_Seek.setValue(round(self.t * 1e6))
        self.Redraw.emit()

    def SetMaxTime(self, max_t: float):
        self.max_t: float = max_t
        self.slider_Seek.setMaximum(round(self.max_t * 1e6))
        self.lbl_MaxTime.setText(
            '<html><head/><body><p><span style=" font-size:10pt;">{:.2f} s</span></p></body></html>'.format(
                self.max_t, 2))

    def GetData(self) -> dict:
        self.dt = self.txt_dt.value()

        data = {}
        data['dt'] = self.dt
        data['A'] = self.txt_A.value()
        data['B'] = self.txt_B.value()
        data['Projectiles'] = {}

        for i, PB in enumerate(self.ProjectileBoxes.values()):
            PB: ProjectileBox

            data['Projectiles'][i] = {
                'x_i': PB.txt_xi.value(),
                'y_i': PB.txt_yi.value(),
                'm': PB.txt_m.value(),
                'v': PB.txt_v.value(),
                'ang': PB.txt_ang.value()
            }
        return data


class ProjectileBox(QtWidgets.QWidget):

    deleted = QtCore.pyqtSignal(int)

    def __init__(self, id):
        super(ProjectileBox, self).__init__()

        __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        uic.loadUi(os.path.join(__location__, 'ProjectileBox.ui'), self)

        #yapf: disable
        self.button_Remove: QtWidgets.QPushButton

        self.txt_xi     : QtWidgets.QDoubleSpinBox
        self.txt_yi     : QtWidgets.QDoubleSpinBox
        self.txt_v      : QtWidgets.QDoubleSpinBox
        self.txt_ang    : QtWidgets.QDoubleSpinBox
        self.txt_m      : QtWidgets.QDoubleSpinBox

        self.id = id
        #yapf: enable

        self.button_Remove.clicked.connect(self._delete)

    def _delete(self):
        self.deleted.emit(self.id)

        parentLay: QtWidgets.QLayout = self.parent().layout()
        parentLay.removeWidget(self)

        self.deleteLater()

        del self