import ctypes as C
import ctypes.util as Cutil
import numpy as np
import math

from astropy.io import fits 


datastore_path="c:/cloudstor/datastore/imaqtest/"

#Find imaq dll drivers
imaqlib_path = Cutil.find_library('imaq')
imaq = C.windll.LoadLibrary(imaqlib_path)

width = 1280
height = 1024
INTERFACE_ID = C.c_uint32
SESSION_ID = C.c_uint32
iid = INTERFACE_ID(0)
sid = SESSION_ID(0)

lcp_cam = C.c_char_p(b'img0') 
rval = imaq.imgInterfaceOpen(lcp_cam, C.byref(iid))

print(rval)

rval = imaq.imgSessionOpen(iid, C.byref(sid))

image = np.zeros((1024*1280),dtype=C.c_uint16)
#image = np.ndarray(shape=(height*width,), dtype=C.c_uint16)

bufAddr = image.ctypes.data_as(C.POINTER(C.c_long))


rval = imaq.imgSnap(sid, C.byref(bufAddr))

#text = C.c_char_p(b'test')
#imaq.imgShowError(rval, text)
#print (text.value)

rval = imaq.imgClose(sid, 1)
rval = imaq.imgClose(iid, 1)


print(image.shape)
print(image)

image2 = np.trim_zeros(image)

print(image2.shape)

#hdu = fits.PrimaryHDU(image)
#hdulist = fits.HDUList([hdu])
#hdulist.writeto(datastore_path + 'test.fits',overwrite=True)
#hdulist.close()