import os
import sys
import uuid
import json

sys.path.append('/FrexT/k8s_handler')  # 导入test文件的绝对路径

from kubernetes import client, config
from websocket_server import WebsocketServer


class k8s_handler:
    def __init__(self):
        # Configs can be set in Configuration class directly or using helper
        # utility. If no argument provided, the config will be loaded from
        # default location.
        config.load_incluster_config()
        self.api_instance = client.BatchV1Api()
        self.namespace = "default"

    def create_job(self, client1, client2):
        data = json.dumps(client1)
        data2 = json.dumps(client2)
        print("client1: ", client1)
        print("client2: ", client2)


        volume_mount = client.V1VolumeMount(
            name="code",
            mount_path="/code",
        )

        # volume definitions
        volume = client.V1Volume(
            name="code",
            host_path=client.V1HostPathVolumeSource(
                path="/mnt/hgfs/0Web/",
                type="Directory",
            )
        )

        container = client.V1Container(
            name="ljw-test-socket-" + uuid.uuid1().__str__(),
            image="socket_test:v0.0.0",
            command=["python"],
            args=[
                "/code/FrexTControlServer/k8s_handler/socket_my.py",
                "-u" + json.dumps(data),
                "-d" + json.dumps(data2),
            ],
            # command=["/bin/sh"],
            # args=["-c", "while true; do echo hello; sleep 10;done"],
            volume_mounts=[
                volume_mount,
            ],
            ports=[
                client.V1ContainerPort(
                    host_port=38000
                ),
            ],
        )

        template = client.V1PodTemplateSpec(
            metadata=client.V1ObjectMeta(),
            spec=client.V1PodSpec(
                restart_policy="Never",
                containers=[container],
                volumes=[
                    volume
                ],
            ),
        )

        spec = client.V1JobSpec(
            template=template,
            backoff_limit=4,
            ttl_seconds_after_finished=100,
        )

        job = client.V1Job(
            api_version="batch/v1",
            kind="Job",
            metadata=client.V1ObjectMeta(
                name="test-job"
            ),
            spec=spec,
        )

        self.api_instance.create_namespaced_job(namespace=self.namespace, body=job)


# Called for every client connecting (after handshake)
def new_client(client, server):
    print("New client connected and was given id %d")
    # server.send_message_to_all(json.dumps({"type": 1000, "info": "new client in"}).encode("utf-8"))


# Called for every client disconnecting
def client_left(client, server):
    print("client disconnected")

if __name__ == "__main__":
    server = WebsocketServer(8014, host="0.0.0.0")
    server.set_fn_new_client(new_client)
    server.set_fn_client_left(client_left)
    server.run_forever()

