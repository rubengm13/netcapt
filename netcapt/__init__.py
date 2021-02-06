from unipath import Path
import os

os.environ['NET_TEXTFSM'] = Path(os.path.dirname(__file__), 'ntc_templates', 'templates')

from .get_network_device import GetNetworkDevice
# from .network_device import NetworkDevice
# This is a test
# And another one
