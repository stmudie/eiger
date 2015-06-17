from FileReaderExampleH5py import createLUT, readImage
import h5py
from PIL import Image
from os.path import basename, dirname
import sys

masterFilename = sys.argv[1]
print masterFilename
try:

    directory = dirname(masterFilename)
    filebase = basename(masterFilename).rsplit('_', 1)[0]

    hdf5File = h5py.File(masterFilename, 'r')

    detector = hdf5File['entry']['instrument']['detector']
    print "entries in detector: ", list(detector)
    LUT = createLUT(hdf5File)
    for imgNr in range(1, len(LUT)+1):
        npimage = readImage(imgNr, LUT, hdf5File)
        tifimage = Image.fromarray(npimage, 'I')
        filename = "{}/tiff/{}_{}.tiff".format(directory, filebase, str(imgNr).zfill(6))
        print filename
        tifimage.save(filename)

except:
    pass
