# -*- coding: utf-8 -*-
"""

@author: kuotiong


"""
import ctypes as C
import ctypes.util as Cutil
import numpy as np
import math
from time import sleep
#import serial

import datetime



class IR_image_session():

       
    def __init__(self):
        '''setting up stuff for the camera/data'''
        imaqlib_path = Cutil.find_library('imaq')
        self.imaq = C.windll.LoadLibrary(imaqlib_path)
#        super(IR_image_session,self).__init__()
        
   
    def cameraInit(self, expos=1.0):
        """initiate the session, expos is requested exposure time in seconds"""
        # Define the number of buffers
        self.frame_time = 0.0167
        self.expos_time=expos
        self.frameNum = int(math.ceil(expos/self.frame_time))
        self.bufNum = self.frameNum
        self.exptime = self.bufNum*self.frame_time
        
        # The next line is to get the # of bytes per pixel. I think that we talked 
        # about this a few days ago and decided that we didn't understand the numbers
        # asigned to these variables. I am going to use 2 like in imaq_trial files
        byteperpix = 2
        self.width = 1280
        self.height = 1024
        self.bufSize = byteperpix * self.width * self.height 
        INTERFACE_ID = C.c_uint32
        SESSION_ID = C.c_uint32
        self.iid = INTERFACE_ID(0)
        self.sid = SESSION_ID(0)

        imgbuffer = C.POINTER(C.c_uint16)()

        lcp_cam = 'img0'  # replace this with the correct camera name 
        rval = self.imaq.imgInterfaceOpen(lcp_cam, C.byref(self.iid))


        rval = self.imaq.imgSessionOpen(self.iid, C.byref(self.sid))

   
        ##### data holder #######

        # #These next two lines create the array of pointers for the buffer
        imgbuffer = C.POINTER(C.c_uint16)*self.bufNum

        # #creates a list of empty buffers
        self.bufList = imgbuffer()

        # #This code automatically assigns buffer etc., therefore all the other code we had about buffers is unnecessary
        self.rval = self.imaq.imgRingSetup(self.sid, self.bufNum, self.bufList, 0, 0 )
             
        
        print('Camera Initialized')
   
    
    def expos(self):
        """
        fill the buffers and return a science frame
        """
        
        
        self.start_time = ("""%s""" % datetime.datetime.utcnow()).replace(' ','T')

#        unstacked = np.empty((300,240,320),dtype='uint16')

#        medianList=[]       
#        data=np.zeros((240,320))
        flat_data = np.zeros((1024,1280),dtype='uint16')
        for i in range(int(self.expos_time)):  #allows integer values of longer than one second
        # #Use this to see individual frames
                

#        dataList=[]
        # start filling the buffers
            rval = self.imaq.imgSessionStartAcquisition(self.sid)

            sleep(1.1)
            
            rval = self.imaq.imgSessionStopAcquisition(self.sid)

            
            
            for j in range(60):  #gives one second of data
                np_buffer = np.core.multiarray.int_asbuffer(C.addressof(self.bufList[j].contents), self.bufSize)
                flat_data+=np.reshape(np.frombuffer(np_buffer,dtype='uint16'),(1024,1280))

#                unstacked[(i*60)+j]=buf
#                print np.median(unstacked)                


#got rid of this median correction stuff.  could be reimplemented later
#            med=np.median(flat_data)
#            med_reduced_data=flat_data/med
#            medianList.append(med)
#            data+=med_reduced_data
            
#            x = np.frombuffer(np_buffer,dtype=np.uint16)
            
#            flat_data += x
#            dataList.append(np.array(x))
            
            self.stop_time = ("""%s""" % datetime.datetime.utcnow()).replace(' ','T')
        
                
        
             # #These next two lines create the array of pointers for the buffer
            imgbuffer = C.POINTER(C.c_uint16)*self.bufNum

        # #creates a list of empty buffers
            self.bufList = imgbuffer()

       
            self.rval = self.imaq.imgRingSetup(self.sid, self.bufNum, self.bufList, 0, 0 )         
        
        self.img=flat_data
#        self.img = data*np.median(medianList)
#        self.img_raw=unstacked
#        self.dList=dataList        
                
        
       # ser = serial.Serial(port =0, baudrate = 9600)
        #ser.write("camera:temp?\r")
        #self.TEMP = int(ser.read(15)[13:])
        #ser.close()

    def close(self):
        """
        just close the session
        """
        rval = self.imaq.imgClose(self.sid, 1)
        rval = self.imaq.imgClose(self.iid, 1)
        
        print('camera interface closed')

if __name__ == "__main__":
    camera = IR_image_session()