
import logging
import uuid

import thread

import MemberList
import Util
from MemberList import MemberList
from Util import *

logging.basicConfig(format='%(asctime)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S',
                    level=logging.INFO,
                    filemode='w',
                    filename = 'logFile_' + str(int(time.time()))
                    )
LOGGER = logging.getLogger("main")

member_list_lock = thread.allocate_lock()

class Talker(object):

    def __init__(self, spread_type):
        super(Talker, self).__init__()

        self.ip = Util.find_my_ip()
        temp_id = uuid.uuid1()
        self.id = str(self.ip) + '_' + str(temp_id.int)[:5]
        self.status = 'JOINED'
        self.timestamp = time.time()
        self.heartbeat = 1
        self.membershipList = MemberList(self)
        # why need tuple for spreadType, we need this later for changing spread type
        self.spread_type = (spread_type, time.time())


    def grouptalk(self):
        
        while True:
            # we need this lock to avoid deadlock 
            member_list_lock.acquire()

            if self.status == 'JOINED' or self.status == TO_QUIT:
                # refresh first in here to take care of the potential fail and fail before talking to others
                self.membershipList.refresh()
                self.heartbeat_increment()
                message = self.membershipList.rumerGeneration()
                message = {'spread_type': self.spread_type, 'message': message}
                memberList = self.membershipList.talkableMembers()

                # generate listener list based on gossip or alltoall
                if self.spread_type[0] == GOSSIP:
                    memberList = random.sample(memberList, min(len(memberList), NUMBER_OF_GOSSIP))
                self.sendMessageToEveryone(message, memberList)

                if (self.membershipList.members[INTRODUCER_IP][STATUS] == TO_QUIT and self.ip != INTRODUCER_IP):
                    self.membershipList.members[INTRODUCER_IP] = {
                        HEARTBEAT: 0,
                        STATUS: NEW_GRAD,
                        TIMESTAMP: 0
                    }

                if self.status == 'JOINED':
                    # everytime I send out a message to others, I will clean my list if my memberlist is changing to TO_QUIT

                    self.membershipList.toQuitRefresh()

                elif self.status == TO_QUIT:
                    # if I change my status to TO_QUIT, then I will change it to afterquit in order to quit
                    self.status = AFTER_QUIT

            member_list_lock.release()
            # everytime I wait 0.2 seconds in order to send another messge
            time.sleep(float(TALK_REST_INTERVAL))




    def sendMessageToEveryone(self, message, memberList):
        logging.info('This is the MemberList: \n'+ str(memberList) + '\n')
        logging.info('This is the message I am going to send to above Memberlist  : \n'+ str(message)+ '\n')

        for memberIp in memberList:
            # I dont send message to myself
            if memberIp == self.id.split('_')[0]:
                continue
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

                sock.sendto(json.dumps(message), (memberIp, PORT_NUMBER))

            except Exception:
                pass

    def heartbeat_increment(self):
        self.heartbeat += 1
        self.timestamp = time.time()


    def listen(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((self.ip, PORT_NUMBER))
        while self.status == 'JOINED':
            payload = json.loads(sock.recvfrom(2048)[0].strip())
            logging.info('This is the Rumor I receive: \n'+ str(payload)+ '\n')

            rumor = payload['message']
            spreadType = payload['spread_type']
            # this part is to decide if I need to change the spreadType
            prev = self.spread_type[0]
            if self.spread_type[0] == UNKNOWN and spreadType[0] != UNKNOWN:
                self.spread_type = spreadType
            elif spreadType[0] != UNKNOWN and spreadType[1] > self.spread_type[1]:
                self.spread_type = spreadType
            after = self.spread_type[0]
            if prev != after:
                logging.info("I am changing spread type to " + after)
                print("I am changing spread type to " + after)
            if rumor:
                member_list_lock.acquire()

                self.membershipList.merge(rumor)
                member_list_lock.release()


    def run(self):
        thread.start_new_thread(self.grouptalk, ())
        thread.start_new_thread(self.listen, ())
        while True:
            cmd = raw_input(' type "list" to show membership list\n type "my_id" to show the id of the local vm \n type "leave" to let the program voluntarily leave\n')
            if cmd in ['gossip', 'alltoall']:
                member_list_lock.acquire()
                if cmd == 'gossip':
                    self.spread_type = (GOSSIP, time.time())
                else:
                    self.spread_type = (ALLTOALL, time.time())
                member_list_lock.release()
            elif cmd == 'list':
                print(self.membershipList)

            elif cmd == 'leave':
                member_list_lock.acquire()

                self.status = TO_QUIT
                member_list_lock.release()

                logging.info('I am leaving ')

                while self.status != AFTER_QUIT:
                    pass
                logging.info('I left ')
                break

            elif cmd == 'my_id':
                print(self.id)

            else:
                print('Please enter something that is vali')



if __name__ == '__main__':
    cmd = '-1'
    while True:
        cmd = raw_input('Please define what spread type you want\n 1:Unknown \n2: gossip \n3: AlltoAll')

        if cmd not in ['1', '2', '3']:
            continue
        else:
            break

    mapper = {'1': UNKNOWN, '2' : GOSSIP, '3' : ALLTOALL}

    gossiper = Talker(mapper[cmd])
    gossiper.run()
