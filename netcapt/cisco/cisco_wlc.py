from .cisco import CiscoNetworkDevice
from .. import utils
import re
from ..netcapt_exceptions import GatherAttributeUnsupported
from ..supported_attr import UnsupportWirelessControllerAttr


class CiscoWlcDevice(CiscoNetworkDevice, UnsupportWirelessControllerAttr):
    def gather_ap(self):
        """
        Gather the AP Summary and combine the data with each AP Gather
        :return:
        """
        ap_sum = self.send_command('show ap summary', use_textfsm=True)
        for ap in ap_sum:
            ap_config = self.send_command('show ap config general ' + ap['ap_name'], use_textfsm=True)
            if len(ap_config) == 1:
                ap.update(ap_config[0])
            else:
                raise ValueError(
                    'Command show ap config general ' + ap['ap_name'] +
                    'has more then one entry verify output with TextFSM Template'
                )
        return ap_sum

    def gather_inventory(self):
        inventory = self.send_command('show inventory', use_textfsm=True)
        for line in inventory:
            line['name'] = self.hostname
        inventory += self.send_command('show ap inventory all', use_textfsm=True)
        return inventory

    def gather_version(self):
        gather_output = self.send_command('show sysinfo', use_textfsm=True)
        gather_output[0].update(self.send_command('show inventory', use_textfsm=True)[0])
        return gather_output

    # TODO: Consider if we need to override the cmd_verify per command or just here.
    # def send_command(self, command, cmd_verify=False, **kwargs):
    #     return self.connection.send_command(command_string=command, )
    def show_cdp_neigh_detail(self, use_textfsm=True, cmd_verify=False):
        """
        Captures the Detailed CDP output
        :param use_textfsm: Boolean to determine if TextFSM should be used to parse the output default: True
        :return: List of Detailed CDP Neighbors
        """
        return self.send_command("show cdp neighbors detail", use_textfsm=use_textfsm, cmd_verify=cmd_verify)

    def update_hostname(self):
        """Gets Hostname from the Connection and saves it to the device."""
        prompt = self.connection.find_prompt()
        self.hostname = re.match(r'\((\S+)\)', prompt).group(1)

    def count_intf(self):
        return dict()

