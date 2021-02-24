from .cisco import CiscoNetworkDevice
from .. import functions as hf
from ..supported_attr import UnsupportSwitch


class CiscoNxosDevice(CiscoNetworkDevice, UnsupportSwitch):

    _trunk_dict = {
        'vlans_native': 'cisco_nxos_get_intf_native_vlan.textfsm',
        'vlans_allowed': 'cisco_nxos_get_intf_allowed_vlan.textfsm',
        'vlans_forwarding': 'cisco_nxos_get_intf_trunk_vlan.textfsm',
        'vlans_not_pruned': 'cisco_nxos_get_intf_not_pruned_vlan.textfsm',
    }

    def gather_arp(self):
        """
        Captures arp information and utilizing the vrf data it parses the
        output to prepare it for extraction to WB.
        """
        vrf_list = self.get_vrf_names()
        arp_list = list()
        for vrf in vrf_list:
            command = "show ip arp"
            if vrf != "global":
                command += " vrf " + vrf
            output = self.send_command(command, use_textfsm=True)
            if isinstance(output, list):
                for arp in output:
                    assert isinstance(vrf, object)
                    arp["vrf"] = vrf
                    # this is NXOS specific
                    arp["type"] = "ARPA"
                    arp_list.append(arp)
            else:
                arp = {'vrf': vrf, 'address': "No ARP Data Found"}
                arp_list.append(arp)
        return arp_list

    def gather_route(self):
        vrf_names = self.get_vrf_names()
        route_list = list()
        for vrf in vrf_names:
            route_list += self.send_command('show ip route vrf %s' % vrf)

    def get_vrf_info(self):
        return self.show_vrf_interface()

    def show_vrf_interface(self, use_textfsm=True):
        return self.send_command('show vrf interface', use_textfsm=use_textfsm)

