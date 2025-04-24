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
        self.running = True  
        self.callback = None  

    def run(self):
        self.chan.bind(self.client)
        self.server = self.chan.subgroup('server')  

    def stop(self):
        self.running = False  
        self.chan.leave('client')

    def append(self, data, db_list, callback):  
        assert isinstance(db_list, DBList)
        self.callback = callback  
        msg = (constRPC.APPEND, data, db_list)  
        self.chan.send_to(self.server, msg)  
        ack = self.chan.receive_from(self.server)
        if (ack[1] == "ACK"):
            print("ACK received, continue working...")  
            threading.Thread(target=self.listen_for_results).start()
        print(ack[1])

    def listen_for_results(self):  
        while self.running:  
            msg = self.chan.receive_from_any(timeout=1)  
            if msg and msg[1][0] == 'RESULT':  
                _, result = msg[1]  
                if self.callback:  
                    self.callback(result)  
                    self.callback = None  





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
                self.chan.send_to({client}, ('ACK'))  
                threading.Thread(target=self.process_request, args=(client, msgrpc)).start()  

    def process_request(self, client, msgrpc):  
        time.sleep(10)  
        if constRPC.APPEND == msgrpc[0]:  
            result = self.append(msgrpc[1], msgrpc[2])  
            self.chan.send_to({client}, ('RESULT', result))  


