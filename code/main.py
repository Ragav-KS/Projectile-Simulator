import sys

from matplotlib import axes
from matplotlib.figure import Figure
from PyQt5 import QtCore, QtWidgets
from scipy import constants as Cn

from Solver import Projectile
from ui import Ui

# Constants

#yapf: disable
t           : float     = 0
dt          : float     = 0.025
A           : float     = 4e-5
B           : float     = 0

g           : float     = Cn.g
v           : float     = 0

Projectiles : dict      = {}
lineList    : dict      = {}

max_xrange  : list      = [0, 1]
max_yrange  : list      = [0, 1]
max_time    : float     = 0
bgCache                 = None

fig         : Figure
ax          : axes
#yapf: enable


def PrepareFigure():
    global fig, ax

    fig = MyUI.canvas.fig
    ax = fig.gca()

    ax.cla()
    ax.yaxis.grid(color='gainsboro', linestyle='dotted', linewidth=1.5)
    ax.xaxis.grid(color='gainsboro', linestyle='dotted', linewidth=0.8)
    ax.axhline(0, linestyle='dotted', color='grey')
    ax.axvline(0, linestyle='dotted', color='grey')

    ax.set_title('Projectile Trajectory')
    ax.set_xlabel(r'$x$', loc='center')
    ax.set_ylabel(r'$y$', loc='center', rotation=0)

    # fig.tight_layout(h_pad=2, w_pad=1)
    fig.tight_layout()


def LoadData():
    global dt, A, B, Projectiles

    dt, A, B, Prjtls = MyUI.GetData().values()

    Projectiles = {}

    for id, Prjctl in Prjtls.items():
        projectile = Projectile(dt, A, B, Prjctl['m'], Prjctl['x_i'],
                                Prjctl['y_i'], Prjctl['v'], Prjctl['ang'], g)
        Projectiles[id] = projectile


def ProcessData():
    global Projectiles, max_xrange, max_yrange, max_time

    max_xrange = [0, 1]
    max_yrange = [0, 1]

    for Prjctl in Projectiles.values():
        Prjctl: Projectile

        Prjctl.Solve()

        max_time = max(max_time, Prjctl.getMaxTime())

        xr = Prjctl.getMaxXRange()

        yr = Prjctl.getMaxYRange()

        max_xrange[0] = min(xr[0], max_xrange[0])
        max_xrange[1] = max(xr[1], max_xrange[1])

        max_yrange[0] = min(yr[0], max_yrange[0])
        max_yrange[1] = max(yr[1], max_yrange[1])

    set_range()


def set_range():
    global max_xrange, max_yrange

    # set aspect

    # padding
    d = (max_xrange[0] - max_xrange[1]) * 0.08
    max_xrange[0] = max_xrange[0] + d
    max_xrange[1] = max_xrange[1] - d

    d = (max_yrange[0] - max_yrange[1]) * 0.08
    max_yrange[0] = max_yrange[0] + d
    max_yrange[1] = max_yrange[1] - d


def plot_points(animated: bool = False):
    global lineList, Projectiles

    for id, Prjctl in Projectiles.items():
        Prjctl: Projectile

        x, y = Prjctl.getResults(slice(0, t))

        lineList[id] = ax.plot(x,
                               y,
                               marker='o',
                               markersize=4,
                               markevery=[-1],
                               label=str(Prjctl.angle),
                               animated=animated)


def update_points(blit: bool = False):
    global t

    for id, Prjctl in Projectiles.items():
        Prjctl: Projectile
        x, y = Prjctl.getResults(slice(0, t))
        lineList[id][0].set_xdata(x)
        lineList[id][0].set_ydata(y)

    if blit == True:
        MyUI.canvas.restore_region(bgCache)
        for id, Prjctl in Projectiles.items():
            Prjctl: Projectile
            ax.draw_artist(lineList[id][0])
        MyUI.canvas.blit(ax.bbox)
    else:
        MyUI.canvas.draw()


def cache_bg():
    global bgCache

    bgCache = MyUI.canvas.copy_from_bbox(ax.bbox)


def RedrawPlots():
    global lineList, ax, max_xrange, max_yrange, t

    timer.stop()
    t = 0

    LoadData()
    ProcessData()

    RefreshPlots()

    ax.set_xlim(tuple(max_xrange))
    ax.set_ylim(tuple(max_yrange))

    ax.legend()

    MyUI.canvas.draw()

    cache_bg()


def RefreshPlots(animated: bool = False):
    global lineList

    for id, line in lineList.items():
        line[0].remove()

    lineList = {}
    ax.set_prop_cycle(None)

    plot_points(animated=animated)

    MyUI.canvas.draw()


def startAnimation():
    timer.start()

    RefreshPlots(animated=True)
    cache_bg()


def stopAnimation():
    timer.stop()
    RefreshPlots()


def animate():
    global dt, t

    t = round(t + dt, 6)

    if t > max_time:
        stopAnimation()

    update_points(blit=True)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    MyUI = Ui()

    MyUI.txt_dt.setValue(dt)
    MyUI.txt_A.setValue(A)
    MyUI.txt_B.setValue(B)

    MyUI.button_Redraw.clicked.connect(RedrawPlots)
    MyUI.button_Run.clicked.connect(startAnimation)
    MyUI.button_Pause.clicked.connect(stopAnimation)

    timer = QtCore.QTimer()
    timer.setInterval(50)
    timer.timeout.connect(animate)

    PrepareFigure()
    RedrawPlots()

    MyUI.showMaximized()
    app.exec_()
