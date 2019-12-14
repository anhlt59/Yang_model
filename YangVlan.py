"""Test."""
from ydk.models.cisco_ios_xe.Cisco_IOS_XE_native import Native
from ydk.services import CRUDService
from ydk.providers import NetconfServiceProvider
from ydk.errors import YModelError
import logging


# Logging setup
logging.basicConfig(
    format="%(asctime)s %(levelname)s:%(name)s: %(message)s",
    level=logging.WARNING,
)
logger = logging.getLogger(__name__)


class VlanCreator():

    def __init__(self, **kwargs):
        """Init 3 layer: provider, service, model."""
        # create provider
        self.provider = NetconfServiceProvider(address=kwargs['address'],
                                               port=kwargs['port'],
                                               username=kwargs['username'],
                                               password=kwargs['password'],
                                               protocol='ssh')
        # create service
        self.service = CRUDService()
        # create model
        self.vlan = Native.Vlan()

    def create_vlan(self, **kwargs):
        """ vid: vlan id
            vname: vlan name
        """
        vlan_list_inst = Native.Vlan.VlanList()
        vlan_list_inst.id = kwargs['vid']
        vlan_list_inst.name = kwargs['vname']
        self.vlan.vlan_list.append(vlan_list_inst)
        
        try:
            self.service.create(self.provider, self.vlan)
            logger.info('Adding VLAN {} success'.format(kwargs['vid']))
            return True
        except YModelError as e:
            logger.error('Model Error: {}'.format(e))
            return False
        except Exception as e:
            logger.error('Error adding VLAN {}: {}'.format(kwargs['vid'], e))
            return False


if __name__ == '__main__':
    creator = VlanCreator(address='1.1.1.1',
                          port=1234,
                          username='test',
                          password='1234')

    creator.create_vlan(vid=100, vname='test1')
    creator.create_vlan(vid=200, vname='test2')
    creator.provider.close()
