import rpc
import logging
from context import lab_logging

lab_logging.setup(stream_level=logging.INFO)

def handle_result(result):  
    print("Callback: Result received:", result.value)  

cl = rpc.Client()
cl.run()

base_list = rpc.DBList({'foo'})
cl.append('bar', base_list, handle_result)  

for i in range(7):  
    print("Client doing other work...")  
    import time; time.sleep(2)  

cl.stop()