"""Convert a BMP screenshot to PNG so it can be viewed."""
import sys, os
os.environ.setdefault('MPLBACKEND', 'Agg')
import matplotlib.image as mpimg
import matplotlib.pyplot as plt

src, dst = sys.argv[1], sys.argv[2]
img = mpimg.imread(src)
plt.imsave(dst, img)
print('wrote', dst, img.shape)
