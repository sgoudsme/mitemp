#!/usr/bin/env python3
"""Demo file showing how to use the mitemp library."""

import argparse
import re
import logging
import sys
import yaml
import os

from btlewrap import available_backends, BluepyBackend, GatttoolBackend, PygattBackend
from mitemp_bt.mitemp_bt_poller import MiTempBtPoller, \
    MI_TEMPERATURE, MI_HUMIDITY, MI_BATTERY
from MqttHandler import MqttHandler
import time


class argMaker:
    def __init__(self, mac):
        self.mac = mac
        self.backend = "bluepy"
        self.verbose = None

def valid_mitemp_mac(mac, pat=re.compile(r"4C:65:A8:[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}")):
    """Check for valid mac adresses."""
    if not pat.match(mac.upper()):
        print('The MAC address "{}" seems to be in the wrong format'.format(mac))
    return mac


def poll(args):
    """Poll data from the sensor."""
    backend = _get_backend(args.backend)
    poller = MiTempBtPoller(args.mac, backend)
    print("Getting data from Mi Temperature and Humidity Sensor")
    return poller.firmware_version(), poller.name(),  poller.parameter_value(MI_BATTERY), poller.parameter_value(MI_TEMPERATURE), poller.parameter_value(MI_HUMIDITY)
#    print("FW: {}".format(poller.firmware_version()))
#    print("Name: {}".format(poller.name()))
#    print("Battery: {}".format(poller.parameter_value(MI_BATTERY)))
#    print("Temperature: {}".format(poller.parameter_value(MI_TEMPERATURE)))
#    print("Humidity: {}".format(poller.parameter_value(MI_HUMIDITY)))


def print_poll(args):
    firmware, name, battery, temp, hum = poll(args)
    print("FW: {}".format(firmware))
    print("Name: {}".format(name))
    print("Battery: {}".format(battery))
    print("Temperature: {}".format(temp))
    print("Humidity: {}".format(hum))

# def scan(args):
#     """Scan for sensors."""
#     backend = _get_backend(args)
#     print('Scanning for 10 seconds...')
#     devices = mitemp_scanner.scan(backend, 10)
#     devices = []
#     print('Found {} devices:'.format(len(devices)))
#     for device in devices:
#         print('  {}'.format(device))


def _get_backend(backend):
    """Extract the backend class from the command line arguments."""
    if backend == 'gatttool':
        backend = GatttoolBackend
    elif backend == 'bluepy':
        backend = BluepyBackend
    elif backend == 'pygatt':
        backend = PygattBackend
    else:
        raise Exception('unknown backend: {}'.format(args.backend))
    return backend


def list_backends(_):
    """List all available backends."""
    backends = [b.__name__ for b in available_backends()]
    print('\n'.join(backends))


def main():
    """Main function.

    Mostly parsing the command line arguments.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--backend', choices=['gatttool', 'bluepy', 'pygatt'], default='gatttool')
    parser.add_argument('-v', '--verbose', action='store_const', const=True)
    subparsers = parser.add_subparsers(help='sub-command help', )

    parser_poll = subparsers.add_parser('poll', help='poll data from a sensor')
    parser_poll.add_argument('mac', type=valid_mitemp_mac)
    parser_poll.set_defaults(func=print_poll)

    # parser_scan = subparsers.add_parser('scan', help='scan for devices')
    # parser_scan.set_defaults(func=scan)

    parser_scan = subparsers.add_parser('backends', help='list the available backends')
    parser_scan.set_defaults(func=list_backends)

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)

    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(0)

    args.func(args)


def mqtt_mess_recv(payload, topic):
    pass


def mqtt_inject():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    config = None
    with open(dir_path + '/config.yaml') as file:
        config = yaml.full_load(file)

    mqtt = MqttHandler(config['mqtt_broker'], None, config['mqtt_username'], config['mqtt_password'], mqtt_mess_recv)
    while not mqtt.connected:
        pass

    for sens in config['xiaomi-sensors']:
        print(sens)
        number_of_tries = 0
        while number_of_tries < 10:
            try:
                args = argMaker(sens)
                firmware, name, battery, temp, hum = poll(args)
                sens_name = sens[-5:].replace(":","")
                mqtt.publish('temp/' + sens_name +'/temp', temp, True)
                mqtt.publish('temp/' + sens_name +'/hum', hum, True)
                mqtt.publish('temp/' + sens_name +'/battery', battery, True)
                number_of_tries = 15
            except:
                number_of_tries = number_of_tries + 1
            time.sleep(1)
        if number_of_tries != 15:
            print("error in getting sensor data")
            mqtt.publish('debug', 'Error getting temperature data')
            os.system('sudo reboot')



if __name__ == '__main__':
    #main()
    mqtt_inject()


