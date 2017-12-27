#!/usr/bin/env python

import matplotlib.pyplot as plt
import numpy as np

x = [4, 6, 8]
eventually = [56, 86, 124]
centralized = [110, 171, 235]


plt.plot(x, eventually, 'g', x, centralized, 'r--')
plt.show()
