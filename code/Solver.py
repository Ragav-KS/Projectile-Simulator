import numpy as np
import pandas as pd


class Projectile:
    def __init__(self, dt: float, A: float, B: float, m: float, xi: float,
                 yi: float, vi: float, angle: float, g: float) -> None:
        #yapf: disable
        self.dt         : float = dt
        self.A          : float = A
        self.B          : float = B
        self.m          : float = m
        self.xi         : float = xi
        self.yi         : float = yi
        self.vi         : float = vi
        self.angle      : float = angle
        self.g          : float = g

        self.isSolved   : bool  = False

        self.v          : float = 0

        self.result_dict: dict  = {}
        #yapf: enable

    def Solve(self):

        V = lambda v_x, v_y: np.sqrt(v_x**2 + v_y**2)

        def fv(t, x, v_x):
            return v_x

        def fa(t, x, v_x):
            return (-self.A * self.v * v_x)

        def gv(t, x, v_y):
            return v_y

        def ga(t, x, v_y):
            return (-self.g - self.A * self.v * v_y)

        v_x = self.vi * np.cos(np.radians(self.angle))
        v_y = self.vi * np.sin(np.radians(self.angle))

        f_rk4 = self.RKG_Generator(F=[fv, fa],
                                   xi=0,
                                   yi=[self.xi, v_x],
                                   h=self.dt,
                                   Bt=self.Butcher_Tableau('Classic-4th'))

        g_rk4 = self.RKG_Generator(F=[gv, ga],
                                   xi=0,
                                   yi=[self.yi, v_y],
                                   h=self.dt,
                                   Bt=self.Butcher_Tableau('Classic-4th'))

        self.v = V(v_x, v_y)

        self.result_dict[0] = (self.xi, self.yi)

        while True:
            self.v = V(v_x, v_y)

            t, x, v_x = next(f_rk4)
            _, y, v_y = next(g_rk4)

            self.result_dict[t] = (x, y)

            if y <= 0:
                self.isSolved = True
                break

        self.result = pd.DataFrame.from_dict(self.result_dict,
                                             orient='index',
                                             columns=['x', 'y'])

    def getResults(self, Slice: slice) -> tuple:
        x = self.result.loc[Slice][['x']].to_numpy()
        y = self.result.loc[Slice][['y']].to_numpy()
        return (x, y)

    def getMaxXRange(self) -> float:
        return (self.result['x'].min(), self.result['x'].max())

    def getMaxYRange(self) -> float:
        return (self.result['y'].min(), self.result['y'].max())

    def getMaxTime(self) -> float:
        return self.result.index[-1]

    def RKG_Generator(self,
                      F: list,
                      xi: float,
                      yi: list,
                      h: float,
                      Bt: dict,
                      PrcF: int = 6) -> tuple:
        yn = yi
        xn = xi
        var = len(yn)
        hk = np.zeros((var, Bt['s']))
        while True:

            hk.fill(0)

            # k_i
            for i in range(Bt['s']):
                xt = xn + Bt['C'][i] * h
                yt = yn.copy()

                yt += hk.dot(Bt['A'][i])
                for m in range(var):
                    hk[m, i] = h * F[m](xt, *yt)

            # y_{n+1}
            for i in range(var):
                yn[i] += np.array(Bt['B']).dot(hk[i])

            xn = round(xn + h, PrcF)

            yield (xn, *yn)

    def Butcher_Tableau(self, method=None):
    #yapf: disable
        if method == None:
            Meth_list = ['Forward Euler',
                        'Explicit Midpoint',
                        'Ralston',
                        'Kutta-3rd',
                        'Classic-4th']
            return Meth_list
        elif method == 'Forward Euler':
            C =  [  0   ]
            A = [[  0   ]]
            B =  [  1   ]
        elif method == 'Explicit Midpoint':
            C =  [  0,      1/2 ]
            A = [[  0,      0   ],
                [  1/2,    0   ]]
            B =  [  0 ,     1   ]
        elif method == 'Ralston':
            C =  [  0,      2/3 ]
            A = [[  0,      0   ],
                [  2/3,    0   ]]
            B =  [  1/4,    3/4 ]
        elif method == 'Kutta-3rd':
            C =  [  0,      1/2,    1   ]
            A = [[  0,      0,      0   ],
                [  1/2,    0,      0   ],
                [  -1,     2,      0   ]]
            B =  [  1/6,    2/3,    1/6 ]
        elif method == 'Classic-4th':
            C =  [  0,      1/2,    1/2,    1   ]
            A = [[  0,      0,      0,      0   ],
                [  1/2,    0,      0,      0   ],
                [  0,      1/2,    0,      0   ],
                [  0,      0,      1,      0   ]]
            B =  [  1/6,    1/3,    1/3,    1/6 ]

        return {'s':    len(C),
                'C':    np.array(C),
                'A':    np.array(A),
                'B':    np.array(B)}
    #yapf: enable