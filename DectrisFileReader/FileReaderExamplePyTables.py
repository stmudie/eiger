#!/usr/bin/python
"""\brief     Example how to read entries from the NeXus header and images using pytables
   \details  
   \author    Michael Rissi
   \author    Contact: support@dectris.com
   \version   0.1
   \date      21.11.2012
   \copyright See General Terms and Conditions (GTC) on http://www.dectris.com
  
"""

import tables
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
    entry = hdf5File.root.entry
   
    ### todo: it's not a list ###
    for link in list(entry):
        datalink = link.__str__()[7:]
        datalink = datalink.split(' ')[0]
        if not(datalink[:4] == 'data'): 
            continue
        
        ### open the link ###
        try:
            data = getattr(entry, datalink)() ## datalink is a string, so have to use getattr to call entry.datalink. In order to open a link in pytables, one has to use __call__() on the external link

        except IOError as exception: ### cannot open link, probably file does not exist
            continue

        
        ### read the image_nr_low and image_nr_high attributes ###
        image_nr_low  = data.attrs.image_nr_low
        image_nr_high = data.attrs.image_nr_high

        for imgNr in range(image_nr_low, image_nr_high+1):
            LUT[imgNr] = (datalink, imgNr-image_nr_low) 
    
    return LUT
        
   

def readImage(imgNr, LUT, hdf5File):
    datalink = ''
    try:
        (datalink,imageNrOffset) = LUT[imgNr]
    except KeyError as e:
        raise ImageReadException('imgNr out of range')
    
    
    data = getattr(hdf5File.root.entry, datalink)()
    ### use slicing access to get images with image number imageNrOffset ###
    image = data[imageNrOffset, : , : ] ## z / y / x
    return image ## is a numpy array





def main():
    if len(sys.argv) != 2:
        print 'usage: ', sys.argv[0], '<hdf5 master file>'
        return -1
    masterFilename = sys.argv[1]
    hdf5File = tables.File(masterFilename, 'r')

    ######### NEXUS HEADER ITEMS #########

    ### example: list all entries in /entry/instrument/detector ###
    detector = hdf5File.root.entry.instrument.detector
    print "entries in detector: ", detector
    
    ### example: get the gain settings ###
    gain_setting = detector.gain_setting
    print "gain setting: ", gain_setting[0] ### remark: In NeXus, data is always
                                            ### stored as arrays, even if the data is scalar. 
    



    ######### IMAGES #########

    ### first create the LUT to find the path to the images ###
    
    LUT = createLUT(hdf5File)

    ### then read the image imgNr ###
    imgNr = 120

    image = readImage(imgNr, LUT, hdf5File)
    
    ### do whatever you want with the image ###
    ### e.g. draw the image ###
    
    if mpl:
        dispImage(image,  max=10, log=False)




if __name__=='__main__':
    main()
   



