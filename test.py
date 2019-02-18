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


snapshot = IR_image_session()

snapshot.cameraInit(1)


snapshot.expos()


hdu = fits.PrimaryHDU(snapshot.img)
hdulist = fits.HDUList([hdu])
hdulist.writeto(datastore_path + 'test.fits')
hdulist.close()
        
snapshot.close()



#imaqlib_path = Cutil.find_library('imaq')
#print(imaqlib_path)
#imaq = C.windll.LoadLibrary(imaqlib_path)