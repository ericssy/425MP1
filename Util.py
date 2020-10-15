
import logging
import socket
import thread
import json
import time
import random




def find_my_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 0))
    print(s.getsockname()[0])
    print(INTRODUCER_IP)
    return s.getsockname()[0]

JOINED = 'JOINED'
ADDED = 'ADDED'
SUSPECTED = 'SUSPECTED'
TO_QUIT = 'TO_QUIT'
QUIT = 'QUIT'
NEW_GRAD = 'NEW_GRAD'
AFTER_QUIT = 'AFTER_QUIT'

HEARTBEAT = 'heartbeat'
TIMESTAMP = 'timestamp'
STATUS = 'status'

POTENTIAL_FAIL = 'POTENTIAL_FAIL'
FAIL = 'FAIL'
POTENTIAL_FAIL_INTERVAL = 2
FAIL_INTERVAL = 4

INTRODUCER_IP = '172.22.94.68'
PORT_NUMBER = 2345

TALK_REST_INTERVAL = 0.2

GOSSIP = 'GOSSIP'
ALLTOALL = 'ALLTOALL'
UNKNOWN = 'UNKNOWN'

NUMBER_OF_GOSSIP = 2
MSG_LOSS_RATE = 5