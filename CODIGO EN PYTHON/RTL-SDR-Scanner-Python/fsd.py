import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from water_fall_class import Waterfall

# Crear una figura y un eje
fig, ax = plt.subplots()
line, = ax.plot([], [], lw=2)

# Límites del eje
ax.set_xlim(0, 2*np.pi)
ax.set_ylim(-1.5, 1.5)

# Inicialización de la función: traza el fondo de cada cuadro
def init():
    line.set_data([], [])
    return line,

# Función de animación: esta se llama secuencialmente
def animate(i):
    x = np.linspace(0, 2*np.pi, 1000)
    y = np.sin(x + i * 0.1)
    line.set_data(x, y)
    return line,

# Crear animación
# frames=50 indica que la animación se detendrá después de 50 cuadros
ani = FuncAnimation(fig, animate, init_func=init, frames=50, interval=20, blit=True)

plt.show()
