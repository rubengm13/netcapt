from .cisco import CiscoNetworkDevice
from .. import functions as hf


class TextFsmParseIssue(Exception):
    pass


class CiscoWlcDevice(CiscoNetworkDevice):
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

