#!/usr/bin/python
"""\brief     Example how to read entries from the NeXus header and images using h5py.
   \details   This example code shows how to read header items and images written by a Dectris EIGER detector using python and h5py. 
   \author    Michael Rissi
   \author    Contact: support@dectris.com
   \version   0.1
   \date      21.11.2012
   \copyright See General Terms and Conditions (GTC) on http://www.dectris.com
  
"""

import h5py
import sys
import numpy 
mpl = False
try:
    import matplotlib.pyplot as plt
    import matplotlib.cm as cm
    mpl = True
except ImportError:
    print "matplotlib not available"
    

def dispImage(img,min=0,max=1024, log=True):
    ## image plotter ##
      plt.ion()
      if img is None: return
      figure = plt.figure(figsize=(16,4))
      if log:
          img = numpy.log(img)
      pltimg = img.astype(numpy.float32)
      im = plt.imshow(pltimg,cmap=cm.hot)
      plt.colorbar()
      im.set_clim(min,max)
      plt.draw()
      raw_input("press enter to continue")
      
      return figure


class ImageReadException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


def createLUT(hdf5File):
    LUT = {}
    entry = hdf5File['entry']['data']
    
    for datalink in list(entry):
        if not(datalink[0:4] == 'data'): 
            continue
        
        ### open the link ###
        try:
            data = entry[datalink]
        except KeyError as exception: ### cannot open link, probably file does not exist
            continue

        
        ### read the image_nr_low and image_nr_high attributes ###
        image_nr_low  = data.attrs['image_nr_low']
        image_nr_high = data.attrs['image_nr_high']

        for imgNr in range(image_nr_low, image_nr_high+1):
            LUT[imgNr] = (datalink, imgNr-image_nr_low) 
    
    return LUT
        
   

def readImage(imgNr, LUT, hdf5File):
    datalink = ''
    try:
        (datalink,imageNrOffset) = LUT[imgNr]
    except KeyError as e:
        raise ImageReadException('imgNr out of range')
    
    
    data = hdf5File['entry']['data'][datalink]
    ### use slicing access to get images with image number imageNrOffset ###
    image = data[imageNrOffset, : , : ] ## z / y / x
    return image ## is a numpy array





def main():
    if len(sys.argv) != 2:
        print 'usage: ', sys.argv[0], '<hdf5 master file>'
        return -1
    masterFilename = sys.argv[1]
    hdf5File = h5py.File(masterFilename, 'r')

    ######### NEXUS HEADER ITEMS #########

    ### example: list all entries in /entry/instrument/detector ###
    detector = hdf5File['entry']['instrument']['detector']
    print "entries in detector: ", list(detector)
    
    ### example: get the gain settings ###
    # gain_setting = detector['gain_setting']
    # print "gain setting: ", gain_setting[0] ### remark: In NeXus, data is always
                                            ### stored as arrays, even if the data is scalar. 
    




    ######### IMAGES #########

    ### first create the LUT to find the path to the images ###
    
    LUT = createLUT(hdf5File)

    ### then read the image imgNr ###
    imgNr = 1

    image = readImage(imgNr, LUT, hdf5File)
    
    ### do whatever you want with the image ###
    ### e.g. draw the image ###
    
    if mpl:
        dispImage(image,  max=10, log=False)




if __name__=='__main__':
    main()
   



