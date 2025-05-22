import zmq
import time
import random
import constPipe

context = zmq.Context()
socket = context.socket(zmq.PUSH)
socket.bind(f"tcp://*:{constPipe.SPLITTER_OUT_PORT}")

sentences = [
    "Hello world",
    "This is a test",
    "ZeroMQ is great",
    "Python is awesome",
    "Distributed systems are fun",
    "Concurrency is key",
    "Network programming is interesting",
    "Data processing is important",
    "Load balancing is essential",
    "Scalability matters",
    "Fault tolerance is crucial",
    "Performance optimization is necessary",
    "Security is vital",
    "APIs are useful",
    "Microservices are popular",
    "Cloud computing is the future",
]

print("Splitter started...")  
time.sleep(1)  # 

for i in range(20):  
    msg = random.choice(sentences)  
    print(f"Splitter sent: {msg}")  
    socket.send_string(msg) 
    time.sleep(0.2)  
