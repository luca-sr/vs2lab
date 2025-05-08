import zmq
import time
import random
import constPipe

context = zmq.Context()
socket = context.socket(zmq.PUSH)
socket.bind(f"tcp://*:{constPipe.SPLITTER_OUT_PORT}")

def read_sentences_from_file(file_name='input.txt'):
    with open(file_name, 'r') as file:
        sentences = file.readlines()
    return [sentence.strip() for sentence in sentences if sentence.strip()]

print("Splitter started...")
time.sleep(1)

sentences = read_sentences_from_file()

for i in range(20):
    if sentences:
        msg = random.choice(sentences)
        print(f"Splitter sent: {msg}")
        socket.send_string(msg)
        time.sleep(0.2)
    else:
        print("No more sentences in the file.")
        break