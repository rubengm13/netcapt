from .cisco import CiscoNetworkDevice
from .. import functions as hf


class TextFsmParseIssue(Exception):
    pass


class CiscoWlcDevice(CiscoNetworkDevice):

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


    # TODO: Consider if we need to override the cmd_verify per command or just here.
    # def send_command(self, command, cmd_verify=False, **kwargs):
    #     return self.connection.send_command(command_string=command, )

    def show_cdp_neigh_detail(self, use_textfsm=True, cmd_verify=False):
        """
        Captures the Detailed CDP output

        :param use_textfsm: Boolean to determine if TextFSM should be used to parse the output default: True

        :return: List of Detailed CDP Neighbors

        """
        return self.send_command("show cdp neighbor detail", use_textfsm=use_textfsm, cmd_verify=cmd_verify)

