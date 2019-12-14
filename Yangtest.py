"""Test."""
from ydk.models.ietf import ietf_interfaces
from ydk.services import CRUDService
from ydk.providers import NetconfServiceProvider
import logging


# Logging setup
logging.basicConfig(
    format="%(asctime)s %(levelname)s:%(name)s: %(message)s",
    level=logging.WARNING,
)
logger = logging.getLogger(__name__)


class ConfigInterface():

    def __init__(self, **kwargs):
        self.address = kwargs['address']
        self.port = kwargs['port'] if 'port' in kwargs.keys() else 830
        self.username = kwargs['username']
        self.password = kwargs['password']

    def __repr__(self):
        return 'ConfigInterface({}:{}, {}/{})'.format(self.address, self.port, self.username, self.password)

    @property
    def provider(self):
        """Create provider."""
        provider = NetconfServiceProvider(address=self.address,
                                          port=self.port,
                                          username=self.username,
                                          password=self.password,
                                          protocol='ssh')
        return provider

    @property
    def service():
        """Create service."""
        return CRUDService()

    @property
    def interfaces(self):
        """Create model."""
        return ietf_interfaces.Interfaces()

    @configIP
    def configIPv4(self, **kwargs):
        self.interface_inst.Ipv4.enabled = True
        self.interface_inst.Ipv4.Address.ip = kwargs['ip']
        if kwargs['netmask']:
            self.interface_inst.Ipv4.Address.netmask = kwargs['netmask']
        elif kwargs['prefix_length']:
            self.interface_inst.Ipv4.Address.prefix_length = kwargs['prefix_length']
        else:
            raise Exception('Missing subnetmask or prefix')

    @configIP
    def configIPv6(self, **kwargs):
        self.interface_inst.Ipv6.enabled = True
        self.interface_inst.Ipv6.Address.ip = kwargs['ip']
        self.interface_inst.Ipv6.Address.prefix_length = kwargs['prefix_length']

    def configIP(f):
        def wrapper(self, **kwargs):
            """ name: 1/0/1
                type: Ethernet
                prefix_length or netmask
            """
            self.interface_inst = ietf_interfaces.Interfaces.Interface()
            self.interface_inst.name = kwargs['name']
            self.interface_inst.enabled = True
            self.interface_inst.type = kwargs['type']
            if kwargs['description']:
                self.interface_inst.description = kwargs['description']
            f(self, **kwargs)
            self.interfaces.append(self.interface_inst)

            try:
                self.service.create(self.provider, self.interfaces)
                logger.info('Config interface {} success'.format(kwargs['name']))
                return True
            except Exception as e:
                logger.error('Error config interface {}: {}'.format(kwargs['name'], e))
                return False
        return wrapper


if __name__ == '__main__':
    interface = ConfigInterface(address='1.1.1.1',
                                port=1234,
                                username='test',
                                password='1234')

    interface.configIPv4(name='1/1/1', type='Ethernet', ip='1.1.1.1', prefix_length=24)
    interface.provider.close()
