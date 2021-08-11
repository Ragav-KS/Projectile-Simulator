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
    def __init__(self):
        super(Ui, self).__init__()

        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        uic.loadUi(os.path.join(__location__, '.\main.ui'), self)

        #yapf: disable
        self.txt_dt                 : QtWidgets.QDoubleSpinBox
        self.txt_A                  : QtWidgets.QDoubleSpinBox
        self.txt_B                  : QtWidgets.QDoubleSpinBox

        self.button_Run             : QtWidgets.QPushButton
        self.button_Pause           : QtWidgets.QPushButton
        self.button_AddProjectile   : QtWidgets.QPushButton
        self.button_Redraw          : QtWidgets.QPushButton

        self.PBoxContainer          : QtWidgets.QWidget
        #yapf: enable

        self.canvas = MplCanvas(self)
        self.Canvas_Layout.addWidget(self.canvas)
        self.addToolBar(QtCore.Qt.TopToolBarArea, NaviBar(self.canvas, self))

        self.PBoxLayout = self.PBoxContainer.layout()

        self.__PBoxCounter = 0

        self.ProjectileBoxes = {}

        self.button_AddProjectile.clicked.connect(self.AddProjectileBox)

        self.AddProjectileBox()

    def deleted(self, id: int):
        del self.ProjectileBoxes[id]

    def AddProjectileBox(self):
        Projbox = ProjectileBox(id=self.__PBoxCounter)

        Projbox.deleted.connect(self.deleted)

        self.ProjectileBoxes[self.__PBoxCounter] = Projbox
        self.PBoxLayout.addWidget(Projbox)

        self.__PBoxCounter += 1

    def GetData(self) -> dict:
        data = {}
        data['dt'] = self.txt_dt.value()
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

        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
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
