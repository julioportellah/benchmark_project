import google.auth
import google.auth.transport.requests
import googleapiclient.discovery
import argparse
import os
import time
from six.moves import input


compute = googleapiclient.discovery.build('compute', 'v1')
image_response = compute.images().getFromFamily(
        project='ubuntu-os-cloud', family='ubuntu-1804-lts').execute()
source_disk_image = image_response['selfLink']
machine_type = "zones/%s/machineTypes/n1-standard-1"% 'us-east1-b'
startup_script = open(
        os.path.join(
            os.path.dirname(__file__), 'startup-script.sh'), 'r').read()

image_url = "http://storage.googleapis.com/gce-demo-input/photo.jpg"
image_caption = "Ready for dessert?"
print(source_disk_image)
bucket = 'jp-benchmark-bucket'

config = {
        'name': 'test-vm-1',
        'machineType': machine_type,

        # Specify the boot disk and the image to use as a source.
        'disks': [
            {
                'boot': True,
                'autoDelete': True,
                'initializeParams': {
                    'sourceImage': source_disk_image,
                }
            }
        ],

        # Specify a network interface with NAT to access the public
        # internet.
        'networkInterfaces': [{
            'network': 'global/networks/default',
            'accessConfigs': [
                {'type': 'ONE_TO_ONE_NAT', 'name': 'External NAT'}
            ]
        }],

        # Allow the instance to access cloud storage and logging.
        'serviceAccounts': [{
            'email': 'default',
            'scopes': [
                'https://www.googleapis.com/auth/devstorage.read_write',
                'https://www.googleapis.com/auth/logging.write'
            ]
        }],

        # Metadata is readable from the instance and allows you to
        # pass configuration from deployment scripts to instances.
        'metadata': {
            'items': [{
                # Startup script is automatically executed by the
                # instance upon startup.
                'key': 'startup-script',
                'value': startup_script
            }, {
                'key': 'url',
                'value': image_url
            }, {
                'key': 'text',
                'value': image_caption
            }, {
                'key': 'bucket',
                'value': bucket
            }]
        }
    }
print('creating vm')
compute.instances().insert(project='benchmarkproject-308623',zone='us-east1-b', body=config).execute()
print('process done')
