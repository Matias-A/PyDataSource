import PyDataSource

ds = PyDataSource.DataSource(exp='xpptut15',run=54)

evt = ds.events.next()

import matplotlib.pyplot as plt
plt.imshow(evt.cspad.image, vmin=-2, vmax=2)
plt.show()


