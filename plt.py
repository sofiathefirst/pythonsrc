import numpy as np

import matplotlib.pyplot as plt

plt.figure(1) 

x = np.linspace(-10, 10, 1000)
y=x*x*x/3-x*x*3/2-10*x+10
plt.plot(x,y)
plt.show()

