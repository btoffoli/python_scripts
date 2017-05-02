import datetime
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Generate Data
time = mdates.drange(datetime.datetime(2010, 1, 1), 
                     datetime.datetime(2011, 1, 1),
                     datetime.timedelta(days=10))
y1 = np.cumsum(np.random.random(time.size) - 0.5)
y2 = np.cumsum(np.random.random(time.size) - 0.5)

# Plot things...
fig = plt.figure()

plt.plot_date(time, y1, 'b-')
plt.plot_date(time, y2, 'g-')

fig.autofmt_xdate()
plt.show()