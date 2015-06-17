import os
import time
from eigertest2 import EigerTest
from redis import StrictRedis

r = StrictRedis()

eiger = EigerTest('10.130.11.111', '80')
downloadpath = '/mnt/data/mythen/20150616'
old_series = ''

if not os.path.exists(downloadpath):
    os.makedirs(downloadpath)
while True:
     try:
        matching = eiger.fileWriterFiles()
     except:
        print "could not get file list"
     time.sleep(1)
     if len(matching)>0:
        try:
            [eiger.fileWriterSave(i, downloadpath ) for i in matching]
        except:
            print "error saveing - noting deleted"
        else:
            print "Downloaded ..."
            for i in matching:
                print i
                #series = i.rsplit('_',1)[0]
                #print 'master'
                #print i.rsplit('_',1)[1]
                #if i.rsplit('_',1)[1] == 'master.h5':
                #    if old_series != '' and series != old_series:
                #        print 'here'
                #        old_series = series
                #        r.lpush('copied:masterfiles', "{}{}".format(downloadpath, i))
            
            [eiger.fileWriterFiles(i, method = 'DELETE') for i in matching]
            print "Deteted " + str(len(matching)) + " file(s)"
