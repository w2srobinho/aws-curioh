import boto3
import time


class EC2:
    def __init__(self, access_key_id, secret_access_key, region_name='sa-east-1', **kwargs):
        self._client = boto3.client(
            'ec2',
             region_name=region_name,
             aws_access_key_id=access_key_id,
             aws_secret_access_key=secret_access_key)

    def client(self):
        return self._client


class Client:
    def __init__(self, ec2_client):
        self.ec2_client = ec2_client
        self.response = None

    def instance_ids(self, tag_name=''):
        self.response = self.ec2_client.describe_instances()
        reservations = self.response['Reservations']
        if not tag_name:
            return [it['Instances'][0]['InstanceId'] for it in reservations]

        return [
            it['Instances'][0]['InstanceId']
            for it in reservations
            if 'Tags' in it['Instances'][0].keys() and
            it['Instances'][0]['Tags'][0].values()]

    def instance_status(self, instance_id):
        self.response = self.ec2_client.describe_instances()
        instance = self._instance_by_id(instance_id)
        status = instance['State']['Name']
        return status

    def _instance_by_id(self, instance_id):
        if not self.response:
            self.response = self.ec2_client.describe_instances()
        reservations = self.response['Reservations']
        for it in reservations:
            instance = it['Instances'][0]
            if instance_id == instance['InstanceId']:
                return instance
        return None

    def start_instance(self, instance_id):
        instance = self._instance_by_id(instance_id)
        if instance['State']['Name'] == 'running':
            return
        if instance['State']['Name'] == 'stopping':
            self._wait_to('stopped', instance_id)

        self.ec2_client.start_instances(InstanceIds=[instance_id])
        self._wait_to('running', instance_id)

    def _wait_to(self, status, instance_id):
        current_status = self.instance_status(instance_id)
        while current_status != status:
            time.sleep(2)
            current_status = self.instance_status(instance_id)

    def reboot_instance(self, instance_id):
        self.ec2_client.reboot_instances(
            InstanceIds=[instance_id])

    def stop_instance(self, instance_id):
        if self.instance_status(instance_id) == 'stopped' or \
                        self.instance_status(instance_id) == 'stopping':
            return

        self.ec2_client.stop_instances(InstanceIds=[instance_id])
        self.response = self.ec2_client.describe_instances()

    def terminate_instance(self, instance_id):
        if self.instance_status(instance_id) == 'terminated':
            return

        self.ec2_client.terminate_instances(InstanceIds=[instance_id])

    def _running(self, tag_name=None, **kwargs):
        response = self.ec2_client.run_instances(**kwargs)
        instance_id = response['Instances'][0]['InstanceId']
        self._wait_to_running(instance_id)
        if tag_name:
            self.ec2_client.create_tags(
                Resources=[instance_id],
                Tags=[{'Key': 'Name', 'Value': tag_name}])
        return instance_id

    def run_instance(self, **kwargs):
        return self._running(**kwargs)

    def instance_public_ip(self, instance_id):
        instance = self._instance_by_id(instance_id)
        if self.instance_status(instance_id) == 'running':
            return instance['PublicIpAddress']
        return ''
