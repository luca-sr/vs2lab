import logging
import random
import time
import threading  #new_line

from constMutex import ENTER, RELEASE, ALLOW, ACTIVE

HEARTBEAT = 'HEARTBEAT'  #new_line

class Process:
    """
    Implements access management to a critical section (CS) via fully
    distributed mutual exclusion (MUTEX).

    Processes broadcast messages (ENTER, ALLOW, RELEASE) timestamped with
    logical (lamport) clocks. All messages are stored in local queues sorted by
    logical clock time.

    Processes follow different behavioral patterns. An ACTIVE process competes 
    with others for accessing the critical section. A PASSIVE process will never 
    request to enter the critical section itself but will allow others to do so.

    A process broadcasts an ENTER request if it wants to enter the CS. A process
    that doesn't want to ENTER replies with an ALLOW broadcast. A process that
    wants to ENTER and receives another ENTER request replies with an ALLOW
    broadcast (which is then later in time than its own ENTER request).

    A process enters the CS if a) its ENTER message is first in the queue (it is
    the oldest pending message) AND b) all other processes have sent messages
    that are younger (either ENTER or ALLOW). RELEASE requests purge
    corresponding ENTER requests from the top of the local queues.

    Message Format:

    <Message>: (Timestamp, Process_ID, <Request_Type>)

    <Request Type>: ENTER | ALLOW  | RELEASE
    """

    def __init__(self, chan):
        self.channel = chan  # Create ref to actual channel
        self.process_id = self.channel.join('proc')  # Find out who you are
        self.all_processes: list = []  # All procs in the proc group
        self.other_processes: list = []  # Needed to multicast to others
        self.queue = []  # The request queue list
        self.clock = 0  # The current logical clock
        self.peer_name = 'unassigned'  # The original peer name
        self.peer_type = 'unassigned'  # A flag indicating behavior pattern
        self.logger = logging.getLogger("vs2lab.lab5.mutex.process.Process")
        self.failed_processes = set()  #new_line
        self.last_heartbeat = {}  #new_line

    def __mapid(self, id='-1'):
        # format channel member address
        if id == '-1':
            id = self.process_id
        return 'Proc-' + str(id)

    def __cleanup_queue(self):
        if len(self.queue) > 0:
            self.queue.sort()
            # There should never be old ALLOW messages at the head of the queue
            while self.queue[0][2] == ALLOW:
                del (self.queue[0])
                if len(self.queue) == 0:
                    break

    def __active_others(self):  #new_line
        return [p for p in self.other_processes if p not in self.failed_processes]  #new_line

    def __request_to_enter(self):
        self.clock = self.clock + 1  # Increment clock value
        request_msg = (self.clock, self.process_id, ENTER)
        self.queue.append(request_msg)  # Append request to queue
        self.__cleanup_queue()  # Sort the queue
        self.channel.send_to(self.__active_others(), request_msg)  # Send request #new_line

    def __allow_to_enter(self, requester):
        if requester in self.failed_processes:  #new_line
            return  #new_line
        self.clock = self.clock + 1  # Increment clock value
        msg = (self.clock, self.process_id, ALLOW)
        self.channel.send_to([requester], msg)  # Permit other

    def __release(self):
        # need to be first in queue to issue a release
        assert self.queue[0][1] == self.process_id, 'State error: inconsistent local RELEASE'

        # construct new queue from later ENTER requests (removing all ALLOWS)
        tmp = [r for r in self.queue[1:] if r[2] == ENTER]
        self.queue = tmp  # and copy to new queue
        self.clock = self.clock + 1  # Increment clock value
        msg = (self.clock, self.process_id, RELEASE)
        # Multicast release notification
        self.channel.send_to(self.__active_others(), msg)  #new_line

    def __allowed_to_enter(self):
        # See who has sent a message (the set will hold at most one element per sender)
        first_in_queue = self.queue[0][1] == self.process_id
        expected = set(self.__active_others())  #new_line
        received = set([req[1] for req in self.queue[1:]])  #new_line
        all_have_answered = expected.issubset(received)  #new_line
        return first_in_queue and all_have_answered

    def __receive(self):
        # Pick up any message
        _receive = self.channel.receive_from(self.__active_others(), 3)  #new_line
        if _receive:
            msg = _receive[1]
            self.last_heartbeat[msg[1]] = time.time()  #new_line

            self.clock = max(self.clock, msg[0])  # Adjust clock value...
            self.clock = self.clock + 1  # ...and increment

            self.logger.debug("{} received {} from {}.".format(
                self.__mapid(),
                "ENTER" if msg[2] == ENTER
                else "ALLOW" if msg[2] == ALLOW
                else "RELEASE" if msg[2] == RELEASE
                else "HEARTBEAT", self.__mapid(msg[1])))  #new_line

            if msg[2] == ENTER:
                self.queue.append(msg)  # Append an ENTER request
                # and unconditionally allow (don't want to access CS oneself)
                self.__allow_to_enter(msg[1])
            elif msg[2] == ALLOW:
                self.queue.append(msg)  # Append an ALLOW
            elif msg[2] == RELEASE:
                # assure release requester indeed has access (his ENTER is first in queue)
                if self.queue and self.queue[0][1] == msg[1] and self.queue[0][2] == ENTER:  #new_line
                    del (self.queue[0])  # Just remove first message #new_line
                else:  #new_line
                    self.logger.warning(f"Ignored RELEASE from {self.__mapid(msg[1])} due to inconsistent queue state.")  #new_line
            elif msg[2] == HEARTBEAT:  #new_line
                pass  #new_line

            self.__cleanup_queue()  # Finally sort and cleanup the queue
        else:
            if self.queue:  #new_line
                self.logger.warning("{} timed out on RECEIVE. Local queue: {}".format(
                    self.__mapid(),
                    list(map(lambda msg: (
                        'Clock '+str(msg[0]),
                        self.__mapid(msg[1]),
                        msg[2]), self.queue))))

    def __send_heartbeats(self):  #new_line
        while True:  #new_line
            self.channel.send_to(self.__active_others(), (self.clock, self.process_id, HEARTBEAT))  #new_line
            time.sleep(0.5)  #new_line

    def __check_heartbeats_loop(self):  #new_line
        while True:  #new_line
            self.__check_heartbeats()  #new_line
            time.sleep(1)  #new_line

    def __check_heartbeats(self):  #new_line
        current_time = time.time()  #new_line
        timeout_threshold = 3  # seconds #new_line
        for proc in self.__active_others():  #new_line
            last_time = self.last_heartbeat.get(proc, 0)  #new_line
            if current_time - last_time > timeout_threshold:  #new_line
                if proc not in self.failed_processes:  #new_line
                    self.logger.warning(f"Assuming process {self.__mapid(proc)} has failed.")  #new_line
                    self.failed_processes.add(proc)  #new_line
                    self.queue = [msg for msg in self.queue if msg[1] != proc]  #new_line
                    self.__cleanup_queue()  #new_line

    def init(self, peer_name, peer_type):
        self.channel.bind(self.process_id)

        self.all_processes = list(self.channel.subgroup('proc'))
        # sort string elements by numerical order
        self.all_processes.sort(key=lambda x: int(x))

        self.other_processes = list(self.channel.subgroup('proc'))
        self.other_processes.remove(self.process_id)

        self.peer_name = peer_name  # assign peer name
        self.peer_type = peer_type  # assign peer behavior

        for proc in self.other_processes:  #new_line
            self.last_heartbeat[proc] = time.time()  #new_line

        self.logger.info("{} joined channel as {}.".format(
            peer_name, self.__mapid()))

    def run(self):
        threading.Thread(target=self.__send_heartbeats, daemon=True).start()  #new_line
        threading.Thread(target=self.__check_heartbeats_loop, daemon=True).start()  #new_line
        while True:
            # Enter the critical section if
            # 1) there are more than one process left and
            # 2) this peer has active behavior and
            # 3) random is true
            if len(self.all_processes) > 1 and \
                    self.peer_type == ACTIVE and \
                    random.choice([True, False]):
                self.logger.debug("{} wants to ENTER CS at CLOCK {}."
                                  .format(self.__mapid(), self.clock))

                self.__request_to_enter()
                while not self.__allowed_to_enter():
                    self.__receive()

                # Stay in CS for some time ...
                sleep_time = random.randint(0, 2000)
                self.logger.debug("{} enters CS for {} milliseconds."
                                  .format(self.__mapid(), sleep_time))
                print(" CS <- {}".format(self.__mapid()))
                time.sleep(sleep_time/1000)

                # ... then leave CS
                print(" CS -> {}".format(self.__mapid()))
                self.__release()
                continue

            # Occasionally serve requests to enter (
            if random.choice([True, False]):
                self.__receive()
