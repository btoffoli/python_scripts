import pandas as pd
from datetime import datetime
from matplotlib import pyplot as plt, style
import numpy as np

#style.user('ggplot')
dtype = [('Col1','int32'), ('Col2','float32'), ('Col3','float32')]
#values = numpy.zeros(20, dtype=dtype)
values = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]], np.int32)
print(type(values))
index = ['Row'+str(i) for i in range(1, len(values)+1)]

df = pd.DataFrame(values, index=index)

plt_obj = df.plot()
#fig = plt.figure()

fig = plt_obj.get_figure()
#plt.show()

fig.savefig('/tmp/lala.png')