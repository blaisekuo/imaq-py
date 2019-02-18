import ctypes as C
import ctypes.util as Cutil
import numpy as np
import math

from astropy.io import fits 


datastore_path="c:/cloudstor/datastore/imaqtest/"

#Find imaq dll drivers
imaqlib_path = Cutil.find_library('imaq')
imaq = C.windll.LoadLibrary(imaqlib_path)

# setup the frame sizer
width = 1280
height = 1024

# variables for the imaq drivers
INTERFACE_ID = C.c_uint32
SESSION_ID = C.c_uint32
iid = INTERFACE_ID(0)
sid = SESSION_ID(0)

#set up string for the frame grabber
# use NI software to set the camera ICD file
# i switch off between the PIRT and image test icd, but they use the same interface string below
lcp_cam = C.c_char_p(b'img0') 

# open interface
rval = imaq.imgInterfaceOpen(lcp_cam, C.byref(iid))


# open session
rval = imaq.imgSessionOpen(iid, C.byref(sid))

# test lines to see the return error code
#text = C.c_char_p(b'test')
#imaq.imgShowError(rval, text)
#print (text.value)

# for the image test icd use C.c_unit8 and 1024x1024
image = np.ndarray(shape=(height,width), dtype=C.c_uint16)


# set up pointer for the buffer
bufAddr = image.ctypes.data_as(C.POINTER(C.c_long))


# take an image snap
rval = imaq.imgSnap(sid, C.byref(bufAddr))


# close session
rval = imaq.imgClose(sid, 1)
rval = imaq.imgClose(iid, 1)

# see the values of the image
# having a problem with the PIRT detector, only able to get value for 1,000,000 pixels
# might be a 14-bit to 16-bit problem?
# need to try assigning just a pointer and reading data in a hex and reconstructing the pixel values
# have some code for this from ealier work on decoding the raw output from WinIRC
print(image.shape)
print(image)

#write the image to a fits file
hdu = fits.PrimaryHDU(image)
hdulist = fits.HDUList([hdu])
hdulist.writeto(datastore_path + 'test.fits',overwrite=True)
hdulist.close()