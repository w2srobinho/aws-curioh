import time


class Client:
    def __init__(self, ec2_client):
        self.ec2_client = ec2_client

    def instance_ids(self, tag_name=''):
        reservations = self.ec2_client.describe_instances()['Reservations']
        if not tag_name:
            return [it['Instances'][0]['InstanceId'] for it in reservations]

        return [
            it['Instances'][0]['InstanceId']
            for it in reservations
            if 'Tags' in it['Instances'][0].keys() and
            it['Instances'][0]['Tags'][0].values()]

    def instance_status(self, instance_id):
        reservations = self.ec2_client.describe_instances()['Reservations']
        status = ''
        for it in reservations:
            instance = it['Instances'][0]
            if instance_id == instance['InstanceId']:
                status = instance['State']['Name']
        return status

    def start_instance(self, instance_id):
        response = self.ec2_client.start_instances(InstanceIds=[instance_id])
        current_status = response['StartingInstances'][0]['CurrentState']['Name']
        while current_status == 'pending':
            time.sleep(2)
            current_status = self.instance_status(instance_id)

    def stop_instance(self, instance_id):
        if self.instance_status(instance_id) == 'stopped' or \
                        self.instance_status(instance_id) == 'stopping':
            return

        self.ec2_client.stop_instances(InstanceIds=[instance_id])

    def terminate_instance(self, instance_id):
        if self.instance_status(instance_id) == 'terminated':
            return

        self.ec2_client.terminate_instances(InstanceIds=[instance_id])

    def _running(self, tag_name=None, **kwargs):
        response = self.ec2_client.run_instances(**kwargs)
        instance_id = response['Instances'][0]['InstanceId']
        if tag_name:
            self.ec2_client.create_tags(
                Resources=[instance_id],
                Tags=[{'Key': 'Name', 'Value': tag_name}])
        return instance_id

    def run_instance(self, **kwargs):
        return self._running(**kwargs)
