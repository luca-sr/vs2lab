import zmq
import sys
from collections import defaultdict
import constPipe

me = sys.argv[1] 
port = constPipe.REDUCER1_PORT if me == "1" else constPipe.REDUCER2_PORT 

context = zmq.Context()
socket = context.socket(zmq.PULL)
socket.bind(f"tcp://*:{port}") 

counts = defaultdict(int)

print(f"Reducer {me} started...")  

while True:
    word = socket.recv_string()
    counts[word] += 1
    print(f"Reducer {me}: {word} -> {counts[word]}")  
