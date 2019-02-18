import ctypes as C
import ctypes.util as Cutil
import numpy as np
import math
from time import sleep
#import serial

import datetime

from astropy.io import fits 

from frame_grabber import IR_image_session

datastore_path="c:/cloudstor/datastore/imaqtest/"

#Find imaq dll drivers
imaqlib_path = Cutil.find_library('imaq')
imaq = C.windll.LoadLibrary(imaqlib_path)

#initialize camera
#frame_time = 0.0167
#expos = 1
#expos_time=expos
#frameNum = int(math.ceil(expos/frame_time))
#bufNum = frameNum
bufNum=1

byteperpix = 2
width = 1280
height = 1024
bufSize = byteperpix * width * height 
INTERFACE_ID = C.c_uint32
SESSION_ID = C.c_uint32
iid = INTERFACE_ID(0)
sid = SESSION_ID(0)

#AcqWinWidth = C.c_char_p

#rval - imaq.niimaquDisable32bitPhysMemLimitEnforcement(sid)

imgbuffer = C.POINTER(C.c_uint16)()

lcp_cam = 'img0'  # replace this with the correct camera name 
rval = imaq.imgInterfaceOpen(lcp_cam, C.byref(iid))


rval = imaq.imgSessionOpen(iid, C.byref(sid))

imgbuffer = C.POINTER(C.c_uint16)*bufNum

bufList = imgbuffer()

rval = imaq.imgRingSetup(sid, bufNum, bufList, 0, 0 )

flat_data = np.zeros((1024,1024),dtype='uint16')

start_time = ("""%s""" % datetime.datetime.utcnow()).replace(' ','T')

#rval = imaq.imgGetCameraAttributeString(sid, 'IMG_ATTR_ROI_WIDTH', AcqWinWidth)

#print(AcqWinWidth)

#imaq.imgSetAttribute2(sid, IMG_ATTR_ROI_WIDTH, width)
#imaq.imgSetAttribute2(sid, IMG_ATTR_ROI_HEIGHT, height)
#imaq.imgSetAttribute2(sid, IMG_ATTR_ROWPIXELS, width) 

#imgbuffer_vpp=C.cast(C.byref(imgbuffer), C.POINTER(C.c_void_p))

#rval = imaq.imgSnap(sid,imgbuffer_vpp)

image = np.ndarray(shape=(1024, 1280), dtype=C.c_uint16)
bufAddr = image.ctypes.data_as(C.POINTER(C.c_long))

#imgSnap (Sid, (void **)&ImaqBuffer); //NI-IMAQ function
rval = imaq.imgSnap(sid, C.byref(bufAddr))

print(bufAddr.contents)

#print(bufList[0].contents)

stop_time = ("""%s""" % datetime.datetime.utcnow()).replace(' ','T')

rval = imaq.imgClose(sid, 1)
rval = imaq.imgClose(iid, 1)

#rval = imaq.imgSessionStartAcquisition(sid)

#sleep(1.1)
            
#rval = imaq.imgSessionStopAcquisition(sid)


np_buffer = np.core.multiarray.int_asbuffer(imgbuffer.contents, bufSize)
flat_data+=np.reshape(np.frombuffer(np_buffer,dtype='uint16'),(1024,1280))

hdu = fits.PrimaryHDU(flat_data)
hdulist = fits.HDUList([hdu])
hdulist.writeto(datastore_path + 'test.fits')
hdulist.close()