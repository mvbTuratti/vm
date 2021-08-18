import csv
import os
import datetime
from multiprocessing import Lock
import sys
import msrest
from azure.iot.hub import DigitalTwinClient

lock = Lock()
iothub_connection_str = "HostName=gaicoz.azure-devices.net;SharedAccessKeyName=iothubowner;SharedAccessKey=ZPFoIUbFXBzRjupPBTCFPSZGDsB8oEf2RQKz5jiQ2G8="
device_id = "rpi"
command_name = "bombas"  
connect_timeout_in_seconds = 3
response_timeout_in_seconds = 245  # Must be within 5-300
def bebida(comando):

    with lock:
        try:
            # Create DigitalTwinClient
            digital_twin_client = DigitalTwinClient.from_connection_string(iothub_connection_str)

            # Invoke command
            invoke_command_result = digital_twin_client.invoke_command(
                device_id, command_name, comando, connect_timeout_in_seconds, response_timeout_in_seconds
            )
            if invoke_command_result:
                print(invoke_command_result)
            else:
                print("No invoke_command_result found")

        except msrest.exceptions.HttpOperationError as ex:
            print("HttpOperationError error {0}".format(ex.response.text),'warning')
        except Exception as exc:
            print("Unexpected error {0}".format(exc),'warning')
        except KeyboardInterrupt:
            print("Sample stopped",'warning')