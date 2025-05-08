import zmq
import sys
import hashlib
import constPipe

me = sys.argv[1]
context = zmq.Context()

receiver = context.socket(zmq.PULL)
receiver.connect(f"tcp://{constPipe.SPLITTER_HOST}:{constPipe.SPLITTER_OUT_PORT}")

sender1 = context.socket(zmq.PUSH)
sender2 = context.socket(zmq.PUSH)
sender1.connect(f"tcp://{constPipe.SPLITTER_HOST}:{constPipe.REDUCER1_PORT}")
sender2.connect(f"tcp://{constPipe.SPLITTER_HOST}:{constPipe.REDUCER2_PORT}")

print(f"Mapper {me} started...")

while True:
    try:
        sentence = receiver.recv_string(flags=zmq.NOBLOCK)
        if sentence:
            print(f"Mapper {me} received: {sentence}")
            for word in sentence.split():
                h = int(hashlib.md5(word.encode()).hexdigest(), 16)
                if h % 2 == 0:
                    sender = sender1
                else:
                    sender = sender2
                sender.send_string(word)
        else:
            continue

    except zmq.Again:
        pass
    except Exception as e:
        print(f"Error in Mapper {me}: {e}")
        break
