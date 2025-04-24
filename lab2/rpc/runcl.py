import rpc
import logging
from context import lab_logging

lab_logging.setup(stream_level=logging.INFO)

def handle_result(result):  # new_code
    print("Callback: Result received:", result.value)  # new_code

cl = rpc.Client()
cl.run()

base_list = rpc.DBList({'foo'})
cl.append('bar', base_list, handle_result)  # new_code

for i in range(5):  # new_code
    print("Client doing other work...")  # new_code
    import time; time.sleep(2)  # new_code

cl.stop()