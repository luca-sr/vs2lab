import constRPC
import threading
import time
from context import lab_channel


class DBList:
    def __init__(self, basic_list):
        self.value = list(basic_list)

    def append(self, data):
        self.value = self.value + [data]
        return self

class Client:
    def __init__(self):
        self.chan = lab_channel.Channel()
        self.client = self.chan.join('client')
        self.server = None
        self.running = True  # new_code
        self.callback = None  # new_code

    def run(self):
        self.chan.bind(self.client)
        self.server = self.chan.subgroup('server')
        threading.Thread(target=self.listen_for_results).start()  # new_code

    def stop(self):
        self.running = False  # new_code
        self.chan.leave('client')

    def append(self, data, db_list, callback):  # new_code
        assert isinstance(db_list, DBList)
        self.callback = callback  # new_code
        msg = (constRPC.APPEND, data, db_list)  # new_code
        self.chan.send_to(self.server, msg)  # new_code
        ack = self.chan.receive_from(self.server)  # new_code
        print("ACK received, continue working...")  # new_code

    def listen_for_results(self):  # new_code
        while self.running:  # new_code
            msg = self.chan.receive_from_any(timeout=1)  # new_code
            if msg and msg[1][0] == 'RESULT':  # new_code
                _, result = msg[1]  # new_code
                if self.callback:  # new_code
                    self.callback(result)  # new_code
                    self.callback = None  # new_code





class Server:
    def __init__(self):
        self.chan = lab_channel.Channel()
        self.server = self.chan.join('server')
        self.timeout = 3

    @staticmethod
    def append(data, db_list):
        assert isinstance(db_list, DBList)
        return db_list.append(data)

    def run(self):
        self.chan.bind(self.server)
        while True:
            msgreq = self.chan.receive_from_any(self.timeout)
            if msgreq is not None:
                client, msgrpc = msgreq
                self.chan.send_to({client}, ('ACK',))  # new_code
                threading.Thread(target=self.process_request, args=(client, msgrpc)).start()  # new_code

    def process_request(self, client, msgrpc):  # new_code
        time.sleep(10)  # new_code
        if constRPC.APPEND == msgrpc[0]:  # new_code
            result = self.append(msgrpc[1], msgrpc[2])  # new_code
            self.chan.send_to({client}, ('RESULT', result))  # new_code


