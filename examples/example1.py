import numpy as np
import gnuplotpy as gp

amplitude = 3.
x = np.linspace(0., 2*3.14, 100)
y = amplitude*np.sin(x)

args = {
    'the_title': 'Example 1',
    'amp': amplitude,
    'x_max': x[-1],
    'filename': 'example1.png'
}
data = [x, y]
gp.gnuplot('example1.gpi', args, data)
