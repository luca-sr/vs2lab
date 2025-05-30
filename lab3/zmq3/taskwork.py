import pickle
import sys
import time

import zmq

import constPipe

me = str(sys.argv[1])
address1 = "tcp://" + constPipe.SRC1 + ":" + constPipe.PORT1  
address2 = "tcp://" + constPipe.SRC2 + ":" + constPipe.PORT2  

context = zmq.Context()
pull_socket = context.socket(zmq.PULL)  

pull_socket.connect(address1)  
pull_socket.connect(address2)  

time.sleep(1) 

print("{} started".format(me))

while True:
    work = pickle.loads(pull_socket.recv())  
    print("{} received workload {} from {}".format(me, work[1], work[0]))
    time.sleep(work[1] * 0.01)  