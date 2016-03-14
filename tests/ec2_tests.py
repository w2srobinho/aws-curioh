import unittest
from unittest import mock

from curioh.ec2 import Client

DESCRIBE_INSTANCES = {
    'Reservations': [
        {
            'Instances': [{
                'InstanceId': 'i-f800157b',
                'State': {'Name': 'running', 'Code': 16},
                'Tags': [{'Key': 'Name', 'Value': 'ONEHub'}]
            }]
        },
        {
            'Instances': [{
                'InstanceId': 'i-88d2d80b',
                'State': {'Name': 'stopped', 'Code': 80}
            }]
        }
    ]}


class ClientTests(unittest.TestCase):
    def setUp(self):
        self.client_mock = mock.Mock()
        self.client_mock.describe_instances.return_value = DESCRIBE_INSTANCES

    def test_instance_ids(self):
        client = Client(self.client_mock)
        expected_ids = ['i-f800157b', 'i-88d2d80b']
        returned_ids = client.instance_ids()

        self.client_mock.describe_instances.assert_called_with()
        self.assertListEqual(returned_ids, expected_ids)

        expected_ids = ['i-f800157b']
        returned_ids = client.instance_ids(tag_name='ONEHub')

        self.client_mock.describe_instances.assert_called_with()
        self.assertListEqual(returned_ids, expected_ids)

    def test_instance_status(self):
        client = Client(self.client_mock)
        expected_status = 'running'
        returned_status = client.instance_status(instance_id='i-f800157b')

        self.client_mock.describe_instances.assert_called_with()
        self.assertEqual(returned_status, expected_status)

        expected_status = 'stopped'
        returned_status = client.instance_status(instance_id='i-88d2d80b')

        self.client_mock.describe_instances.assert_called_with()
        self.assertEqual(returned_status, expected_status)

    def test_start_instance(self):
        class ClientInstanceTest(Client):
            def __init__(self, ec2):
                super(ClientInstanceTest, self).__init__(ec2)
                self.count = 0

            def instance_status(self, instance_id):
                if self.count < 2:
                    self.count += 1
                    return 'pending'
                return 'running'

        client = ClientInstanceTest(self.client_mock)

        instance_status = {
            'StartingInstances': [{'CurrentState': {'Name': 'pending'}}]
        }
        self.client_mock.start_instances.return_value = instance_status
        client.start_instance(instance_id='i-88d2d80b')
        self.client_mock.start_instances.assert_called_with(InstanceIds=['i-88d2d80b'])

        expected_status = 'running'
        returned_status = client.instance_status(instance_id='i-88d2d80b')
        self.assertEqual(returned_status, expected_status)

    def test_stop_instance(self):
        client = Client(self.client_mock)
        client.stop_instance(instance_id='i-f800157b')
        client.stop_instance(instance_id='i-88d2d80b')

        DESCRIBE_INSTANCES['Reservations'][1]['Instances'][0]['State']['Name'] = 'stopping'

        client.stop_instance(instance_id='i-88d2d80b')
        self.client_mock.stop_instances.assert_called_once_with(InstanceIds=['i-f800157b'])

    def test_terminate_instance(self):
        client = Client(self.client_mock)
        client.terminate_instance(instance_id='i-f800157b')

        DESCRIBE_INSTANCES['Reservations'][0]['Instances'][0]['State']['Name'] = 'terminated'

        client.terminate_instance(instance_id='i-f800157b')
        self.client_mock.terminate_instances.assert_called_once_with(InstanceIds=['i-f800157b'])

    def test_run_instance_with_tag_name(self):
        client = Client(self.client_mock)
        self.client_mock.run_instances.return_value = DESCRIBE_INSTANCES['Reservations'][0]
        expected_id = DESCRIBE_INSTANCES['Reservations'][0]['Instances'][0]['InstanceId']
        returned_id = client.run_instance(
            tag_name='curioh',
            ImageId='ami-efc74483',
            MinCount=1,
            MaxCount=1,
            InstanceType='t2.micro',
            KeyName='robot_2')

        self.client_mock.run_instances.assert_called_once_with(
            ImageId='ami-efc74483',
            MinCount=1,
            MaxCount=1,
            InstanceType='t2.micro',
            KeyName='robot_2')

        self.client_mock.create_tags.assert_called_once_with(
            Resources=[expected_id],
            Tags=[{'Key': 'Name', 'Value': 'curioh'}])

        self.assertEqual(returned_id, expected_id)

    def test_run_instance_without_tag_name(self):
        client = Client(self.client_mock)
        self.client_mock.run_instances.return_value = DESCRIBE_INSTANCES['Reservations'][0]
        expected_id = DESCRIBE_INSTANCES['Reservations'][0]['Instances'][0]['InstanceId']
        returned_id = client.run_instance(
            ImageId='ami-efc74483',
            MinCount=1,
            MaxCount=1,
            InstanceType='t2.micro',
            KeyName='robot_2')

        self.client_mock.run_instances.assert_called_once_with(
            ImageId='ami-efc74483',
            MinCount=1,
            MaxCount=1,
            InstanceType='t2.micro',
            KeyName='robot_2')

        self.client_mock.create_tags.assert_not_called()
        self.assertEqual(returned_id, expected_id)
