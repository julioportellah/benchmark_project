import google.auth
import google.auth.transport.requests
import googleapiclient.discovery
import argparse
import os
import time
from six.moves import input
import datetime as dt

def wait_for_operation(compute, project, zone, operation):
    print('Waiting for operation to finish...')
    while True:
        result = compute.zoneOperations().get(
            project=project,
            zone=zone,
            operation=operation).execute()

        if result['status'] == 'DONE':
            print("done.")
            if 'error' in result:
                raise Exception(result['error'])
            return result

        time.sleep(1)


def create_instance(compute, project, zone, name, bucket, machine_name):
    image_response = compute.images().getFromFamily(
        project='ubuntu-os-cloud', family='ubuntu-1804-lts').execute()
    source_disk_image = image_response['selfLink']
    machine_type = "zones/{}/machineTypes/{}".format(zone, machine_name)
    print(machine_type)
    #machine_type = "zones/%s/machineTypes/n1-standard-1" % zone
    startup_script = open(
        os.path.join(
            os.path.dirname(__file__), 'startup-script.sh'), 'r').read()
    image_url = "http://storage.googleapis.com/gce-demo-input/photo.jpg"
    image_caption = "Ready for dessert?"
    config = {
        'name': name,
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

    return compute.instances().insert(
        project=project,
        zone=zone,
        body=config).execute()
    pass


if __name__ == '__main__':
    compute = googleapiclient.discovery.build('compute', 'v1')
    print('Creating instance.')
    print(compute)
    project = 'benchmarkproject-308623'
    zone = 'us-east1-b'
    time_creation = dt.datetime.now()
    machine_type = 'n1-standard-1'
    operation = create_instance(compute,'benchmarkproject-308623','us-east1-b','test-dev-vm',bucket='jp-benchmark-bucket',machine_name= machine_type)
    wait_for_operation(compute, project, zone, operation['name'])
    time_setup = dt.datetime.now()
    delete_request = compute.instances().delete(project=project, zone=zone,instance='test-dev-vm').execute()
    wait_for_operation(compute, project, zone, delete_request['name'])
    
    time_diff = (time_setup - time_creation).total_seconds()
    print(machine_type, time_diff)
 
