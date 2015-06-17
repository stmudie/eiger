from epics import PV, caput, poll
from eigertest2 import EigerTest
from threading import Thread


class EigerCon(object):

    def __init__(self):
        self.eiger = EigerTest('10.130.11.111', '80')
        self.arm_pv = PV('13EIG1:cam1:ARM_CMD', self.epics_cb)
        self.trigger_pv = PV('13EIG1:cam1:TRIGGER_CMD', self.epics_cb)
        self.disarm_pv = PV('13EIG1:cam1:DISARM_CMD', self.epics_cb)
        self.ntrigger_pv = PV('13EIG1:cam1:NTRIGGER', self.epics_cb)
        self.triggermode_pv = PV('13EIG1:cam1:TRIGGER_MODE', self.epics_cb)
        self.sequence_id_pv = PV('13EIG1:cam1:SEQUENCE_ID')


    def epics_cb(self, pvname, value, **kwargs):
        if pvname == '13EIG1:cam1:ARM_CMD':
            if value == 1:
                thread = Thread(target=self.arm)
                thread.start()

        elif pvname == '13EIG1:cam1:TRIGGER_CMD':
            if value == 1:
                thread = Thread(target=self.trigger)
                thread.start()

        elif pvname == '13EIG1:cam1:DISARM_CMD':
           if value == 1:
                thread = Thread(target=self.disarm)
                thread.start()

        elif pvname =='13EIG1:cam1:NTRIGGER':
            thread = Thread(target=self.ntrigger, args=(value,))
            thread.start()

        elif pvname =='13EIG1:cam1:TRIGGER_MODE':
            thread = Thread(target=self.trigger_mode, args=(value,))
            thread.start()



    def arm(self):
        print 'arm'
        try:
            seq_id = self.eiger.arm()['sequence id']
            self.sequence_id_pv.put(seq_id)
        except RuntimeError:
            pass
        except TypeError:
            pass

        self.arm_pv.put(0)

    def trigger(self):
        print 'trigger'
        try:
            self.eiger.trigger()
        except RuntimeError:
            pass

        self.trigger_pv.put(0)

    def disarm(self):
        print 'disarm'
        try:
            self.eiger.disarm()
        except RuntimeError:
            pass

        self.disarm_pv.put(0)


    def ntrigger(self, value):
        print 'ntrigger'
        try:
            self.eiger.setDetectorConfig('ntrigger', value)
        except RuntimeError:
            pass

    def trigger_mode(self, value):
        print 'trigger mode'
        if value == 0:
            string_value = 'ints'
        elif value == 1:
            string_value = 'exts'
        elif value == 2:
            string_value = 'inte'
        elif value == 3:
            string_value = 'exte'
        else:
            return

        try:
            self.eiger.setDetectorConfig('trigger_mode', string_value)
        except RuntimeError:
            pass


if __name__ == "__main__":
    a = EigerCon()
    while True:
        poll(evt=1.e-5, iot=0.1)
