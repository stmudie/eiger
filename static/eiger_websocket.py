from contextlib import closing
from cStringIO import StringIO
import csv
import cPickle as pickle
from autobahn.asyncio.websocket import WebSocketServerProtocol, WebSocketServerFactory
import json

import logging
logging.basicConfig()

from eigerclient import DEigerClient

try:
    import asyncio
    import asyncio_redis
except ImportError:
    ## Trollius >= 0.3 was renamed
    import trollius as asyncio
    from trollius import From


class EigerControlServerProtocol(WebSocketServerProtocol):

    def __init__(self):
        IP = "62.12.129.162"
        PORT = "4011"
        self.eiger = DEigerClient(host=IP, port=PORT, verbose=True)

    def onConnect(self, request):
        print("Client connecting: {0}".format(request.peer))

    def onOpen(self):
        print("WebSocket connection open.")

    def onMessage(self, payload, isBinary):
        print("Message Received")
        payload = json.loads(payload.decode('utf8'))
        getattr(self, "on_{}".format(payload['type']), "on_undefined")(payload)

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))
        # When finished, close the redis async connection.
        try:
            self.connection.close()
        except AttributeError:
            pass

    def on_filewriter(self, payload):
        data = payload['data']
        if data['property'] == 'mode':
            if data['value'] is True:
                data['value'] = 'enabled'
            if data['value'] is False:
                data['value'] = 'disabled'

        self.eiger.setFileWriterConfig(data['property'], data['value'])

    def on_detector(self, payload):
        data = payload['data']
        try:
            result = self.eiger.setDetectorConfig(data['property'], data['value'])
        except RuntimeError:
            return

        result_dict = {}
        for param in result:
            result_dict[param] = self.eiger.detectorConfig(param=param)['value']
        self.sendMessage(json.dumps({'type': 'update', 'data': result_dict}))

    def on_update_all(self, payload):
        # TODO Replace with self.eiger.detectorConfig() to get all with one call. Timing out with remote detector.
        result_dict = {'count_time': 0.0,
                       'frame_time': 0.0,
                       'photon_energy': 0.0,
                       'wavelength': 0.0,
                       'element': '',
                       'threshold_energy': 0.0,
                       'nimages': 0,
                       'flatfield_correction_applied': False,
                       'number_of_excluded_pixels': 0,
                       'countrate_correction_applied': False}
        for param in result_dict.keys():
            result_dict[param] = self.eiger.detectorConfig(param=param)['value']
        self.sendMessage(json.dumps({'type': 'update_detector', 'data': result_dict}))

        result_dict = { 'mode': False,
                        'compression_enabled': False,
                        'name_pattern': '',
                        'nimages_per_file': 0}

        for param in result_dict.keys():
            value = self.eiger.fileWriterConfig(param=param)['value']
            if param == 'mode':
                if value is 'enabled':
                    value = True
                if value is 'disabled':
                    value = False
            result_dict[param] = value
        self.sendMessage(json.dumps({'type': 'update_filewriter', 'data': result_dict}))

    def on_undefined(self, payload):
        print 'Undefinied Function {}'.format(payload['type'])

if __name__ == '__main__':

    try:
        import asyncio
    except ImportError:
        ## Trollius >= 0.3 was renamed
        import trollius as asyncio
        from trollius import From



    factory = WebSocketServerFactory("ws://localhost:9000", debug=False)
    factory.protocol = EigerControlServerProtocol

    loop = asyncio.get_event_loop()
    coro = loop.create_server(factory, '127.0.0.1', 9000)
    server = loop.run_until_complete(coro)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.close()
        loop.close()
        # When finished, close the connection.
