"""
class DEigerClient provides an interface to the REST API of jaun

Author: Volker Pilipp
Contact: volker.pilipp@dectris.com
Version: 0.1
Date: 14/02/2014
Copyright See General Terms and Conditions (GTC) on http://www.dectris.com

"""

import os.path
import httplib
import json
import re
import socket
import fnmatch

Version = '1.2.1'

##
#  class DEigerClient provides a low level interface to the jaun rest api. You may want to use class DCamera instead.
#
class DEigerClient(object):
    def __init__(self, host = '127.0.0.1', port = 80, verbose = False):
        """
        Create a client object to talk to the restful jaun api.
        Args:
            host: hostname of the detector computer
            port: port usually 80 (http)
            verbose: bool value
        """
        super(DEigerClient,self).__init__()
        self._host = host
        self._port = port
        self._version = Version
        self._verbose = verbose

    def setVerbose(self,verbose):
        """ Switch verbose mode on and off.
        Args:
            verbose: bool value
        """
        self._verbose = verbose

    def version(self,module = 'detector'):
        """Get version of a api module (i.e. 'detector', 'filewriter')
        Args:
            module: 'detector' or 'filewriter'
        """
        return self._getRequest(url = '/{0}/api/version/'.format(module))

    def listDetectorConfigParams(self):
        """Get list of all detector configuration parameters (param arg of configuration() and setConfiguration()).
        Convenience function, that does detectorConfig(param = 'keys')
        Returns:
            List of parameters.
        """
        return self.detectorConfig('keys')

    def detectorConfig(self,param = None, dataType = None):
        """Get detector configuration parameter
        Args:
            param: query the configuration parameter param, if None get full configuration, if 'keys' get all configuration parameters.
            dataType: None (= 'native'), 'native' ( return native python object) or 'tif' (return tif data).
        Returns:
            If param is None get configuration, if param is 'keys' return list of all parameters, else return the value of
            the parameter. If dataType is 'native' a dictionary is returned that may contain the keys: value, min, max,
            allowed_values, unit, value_type and access_mode. If dataType is 'tif', tiff formated data is returned as a python
            string.
        """
        return self._getRequest(self._url('detector','config',param),dataType)

    def setDetectorConfig(self, param, value, dataType = None):
        """
        Set detector configuration parameter param.
        Args:
            param: Parameter
            value: Value to set. If dataType is 'tif' value may be a string containing the tiff data or
                   a file object pointing to a tiff file.
            dataType: None, 'native' or 'tif'. If None, the data type is auto determined. If 'native' value
                      may be a native python object (e.g. int, float, str), if 'tif' value shell contain a
                      tif file (python string or file object to tif file).
            *params: Optional list of successive params of the form param0, value0, param1, value1, ...
                     The parameters are set in the same order they appear.
        Returns:
            List of changed parameters.
        """
        return self._putRequest(self._url('detector','config',param), dataType, value)

    def setDetectorConfigMultiple(self,*params):
        """
        Convenience function that calls setDetectorConfig(param,value,dataType = None) for
        every pair param, value in *params.
        Args:
            *params: List of successive params of the form param0, value0, param1, value1, ...
                     The parameters are set in the same order they appear in *params.
        Returns:
            List of changed parameters.
        """
        changeList = []
        p = None
        for x in params:
            if p is None:
                p = x
            else:
                data = x
                changeList += self.setDetectorConfig(param = p, value = data, dataType = None)
                p = None
        return list(set(changeList))

    def listDetectorCommands(self):
        """
        Get list of all commands that may be sent to Eiger via command().
        Returns:
            List of commands
        """
        return self._getRequest(self._url('detector','config','keys'))

    def sendDetectorCommand(self, *commands):
        """
        Send command to Eiger. The list of all available commands is obtained via listCommands().
        Args:
            *command: List of commands to send
        Returns:
            The commands 'arm' and 'trigger' return a dictionary containing 'sequence id'.
            If multiple commands are given a list of return values is returned
        """
        ret = [self._putRequest(self._url('detector','command',parameter = c), dataType = 'native') for c in commands]
        if len(ret) == 1:
            return ret[0]
        else:
            return ret

    def detectorStatus(self, param = 'keys'):
        """Get detector status information
        Args:
            param: query the status parameter param, if 'keys' get all status parameters.
        Returns:
            If param is None get configuration, if param is 'keys' return list of all parameters, else return dictionary
            that may contain the keys: value, value_type, unit, time, state, critical_limits, critical_values
        """
        return self._getRequest(self._url('detector','status',parameter = param))


    def fileWriterConfig(self,param = 'keys'):
        """Get filewriter configuration parameter
        Args:
            param: query the configuration parameter param, if 'keys' get all configuration parameters.
        Returns:
            If param is None get configuration, if param is 'keys' return list of all parameters, else return dictionary
            that may contain the keys: value, min, max, allowed_values, unit, value_type and access_mode
        """
        return self._getRequest(self._url('filewriter','config',parameter = param))

    def setFileWriterConfig(self,param,value):
        """
        Set file writer configuration parameter param.
        Args:
            param: parameter
            value: value to set
        Returns:
            List of changed parameters.
        """
        return self._putRequest(self._url('filewriter','config',parameter = param), dataType = 'native', data = value)

    def fileWriterStatus(self,param = 'keys'):
        """Get filewriter status information
        Args:
            param: query the status parameter param, if 'keys' get all status parameters.
        Returns:
            If param is None get configuration, if param is 'keys' return list of all parameters, else return dictionary
            that may contain the keys: value, value_type, unit, time, state, critical_limits, critical_values
        """
        return self._getRequest(self._url('filewriter','status',parameter = param))

    def fileWriterFiles(self, filename = None, method = 'GET'):
        """
        Obtain file from detector.
        Args:
             filename: Name of file on the detector side. If None return list of available files
             method: Eiger 'GET' (get the content of the file) or 'DELETE' (delete file from server)
        Returns:
            List of available files if 'filename' is None,
            else if method is 'GET' the content of the file.
        """
        if method == 'GET':
            if filename is None:
                return self._getRequest(self._url('filewriter','files'))
            else:
                return self._getRequest(url = '/data/{0}'.format(filename), dataType = 'hdf5')
        elif method == 'DELETE':
            return self._delRequest(url = '/data/{0}'.format(filename))
        else:
            raise RuntimeError('Unknown method {0}'.format(method))

    def fileWriterSave(self,filename,targetDir,regex = False):
        """
        Saves filename in targetDir. If regex is True, filename is considered to be a regular expression.
        Save all files that match filename
        Args:
            filename: Name of source file, evtl. regular expression
            targetDir: Directory, where to store the files
        """
        if regex:
            pattern = re.compile(filename)
            [ self.fileWriterSave(f,targetDir)  for f in self.fileWriterFiles() if pattern.match(f) ]
        elif any([ c in filename for c in ['*','?','[',']'] ] ):
            # for f in self.fileWriterFiles():
            #    self._log('DEBUG ', f, '  ', fnmatch.fnmatch(f,filename))
            [ self.fileWriterSave(f,targetDir)  for f in self.fileWriterFiles() if fnmatch.fnmatch(f,filename) ]
        else:
            targetPath = os.path.join(targetDir,filename)
            with open(targetPath,'wb') as targetFile:
                self._log('Writing ', targetPath)
                targetFile.write(self.fileWriterFiles(filename))
            assert os.access(targetPath,os.R_OK)

    #
    #
    #                Private Methods
    #
    #

    def _log(self,*args):
        if self._verbose:
            print ' '.join([ str(elem) for elem in args ])

    def _url(self,module,task,parameter = None):
        url = "/{0}/api/{1}/{2}/".format(module,self._version,task)
        if not parameter is None:
            url += '{0}'.format(parameter)
        return url

    def _getRequest(self,url,dataType = 'native'):
        if dataType is None:
            dataType = 'native'
        if dataType == 'native':
            mimeType = 'application/json; charset=utf-8'
        elif dataType == 'tif':
            mimeType = 'application/tiff'
        elif dataType == 'hdf5':
            mimeType = 'application/hdf5'
        return self._request(url,'GET',mimeType)

    def _putRequest(self,url,dataType,data = None):
        data, mimeType = self._prepareData(data,dataType)
        # self._log("PUT request: ({0},{1})".format(data,mimeType))
        return self._request(url,'PUT',mimeType, data)

    def _delRequest(self,url):
        self._request(url,'DELETE',mimeType = None)
        return None

    def _request(self, url, method, mimeType, data = None):
        if data is None:
            body = ''
        else:
            body = data
        headers = {}
        if method == 'GET':
            headers = {'Accept':mimeType}
        elif method == 'PUT':
            headers =  {'Content-type': mimeType}

        self._log('sending request to {0}'.format(url))
        connection = httplib.HTTPConnection(self._host,self._port)
        try:
            connection.request(method,url, body = data, headers = headers)
        except socket.error as socketError:
            raise RuntimeError(str(socketError))
        except httplib.HTTPException as httpError:
            raise RuntimeError(str(httpError))

        response = connection.getresponse()
        status = response.status
        reason = response.reason
        data = response.read()
        mimeType = response.getheader('content-type','text/plain')
        connection.close()
        self._log('Return status: ', status, reason)
        if not response.status in range(200,300):
            raise RuntimeError((reason,data))
        if 'json' in mimeType:
            return json.loads(data)
        else:
            return data

    def _prepareData(self,data, dataType):
        if data is None:
            return '', 'text/html'
        if dataType != 'native':
            if type(data) == file:
                data = data.read()
            if dataType is None:
                mimeType = self._guessMimeType(data)
                if not mimeType is None:
                    return data, mimeType
            elif dataType == 'tif':
                return data, 'application/tiff'
        mimeType = 'application/json; charset=utf-8'
        return json.dumps({'value':data}), mimeType

    def _guessMimeType(self,data):
        if type(data) == str:
            if data.startswith('\x49\x49\x2A\x00') or data.startswith('\x4D\x4D\x00\x2A'):
                self._log('Determined mimetype: tiff')
                return 'application/tiff'
            if data.startswith('\x89\x48\x44\x46\x0d\x0a\x1a\x0a'):
                self._log('Determined mimetype: hdf5')
                return 'application/hdf5'
        return None


