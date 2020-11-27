from netcapt.cisco.cisco import CiscoNetworkDevice


class CiscoIosDevice(CiscoNetworkDevice):
    def __str__(self):
        return "<Cisco IOS Device> host: {self.host}".format(self=self)
