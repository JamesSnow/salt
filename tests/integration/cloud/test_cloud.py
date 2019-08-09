# -*- coding: utf-8 -*-
'''
Integration tests for functions located in the salt.cloud.__init__.py file.
'''

# Import Python Libs
from __future__ import absolute_import, print_function, unicode_literals
import os

# Import Salt Testing libs
from tests.integration.cloud.helpers.cloud_test_base import CloudTest
from tests.support.helpers import expensiveTest
from tests.support.runtests import RUNTIME_VARS

# Import Salt libs
import salt.cloud


class CloudClientTestCase(CloudTest):
    '''
    Integration tests for the CloudClient class. Uses DigitalOcean as a salt-cloud provider.
    '''

    @expensiveTest
    def setUp(self):
        self.config_file = os.path.join(RUNTIME_VARS.TMP_CONF_CLOUD_PROVIDER_INCLUDES,
                                        'digitalocean.conf')
        self.provider_name = 'digitalocean-config'
        self.image_name = '14.04.5 x64'

        # Use a --list-images salt-cloud call to see if the DigitalOcean provider is
        # configured correctly before running any tests.
        images = self.run_cloud('--list-images {0}'.format(self.provider_name))

        if self.image_name not in [i.strip() for i in images]:
            self.skipTest(
                'Image \'{0}\' was not found in image search. Is the {1} provider '
                'configured correctly for this test?'.format(
                    self.provider_name,
                    self.image_name
                )
            )

    def test_cloud_client_create_and_delete(self):
        '''
        Tests that a VM is created successfully when calling salt.cloud.CloudClient.create(),
        which does not require a profile configuration.

        Also checks that salt.cloud.CloudClient.destroy() works correctly since this test needs
        to remove the VM after creating it.

        This test was created as a regression check against Issue #41971.
        '''
        cloud_client = salt.cloud.CloudClient(self.config_file)

        # Create the VM using salt.cloud.CloudClient.create() instead of calling salt-cloud
        ret_val = cloud_client.create(
            provider=self.provider_name,
            names=[self.instance_name],
            image=self.image_name,
            location='sfo1', size='512mb', vm_size='512mb'
        )

        # Check that the VM was created correctly
        self.assertInstanceExists(ret_val)

        # Clean up after ourselves and delete the VM
        deleted = cloud_client.destroy(names=[self.instance_name])

        # Check that the VM was deleted correctly
        self.assertIn(self.instance_name, deleted)
