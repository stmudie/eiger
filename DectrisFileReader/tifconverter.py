from FileReaderExampleH5py import createLUT, readImage
import h5py
from PIL import Image
from os.path import basename, dirname
from redis import StrictRedis

r = StrictRedis()

while True:

    masterFilename = r.brpoplpush('copied:masterfiles', 'converted:masterfiles')

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

            tifimage.save("{}/tiff/{}_{}.tiff".format(directory, filebase, str(imgNr).zfill(6)))

    except:
        pass
