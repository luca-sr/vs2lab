import logging
import threading
import unittest
import time

import clientserver
from context import lab_logging

lab_logging.setup(stream_level=logging.INFO)
logger = logging.getLogger("vs2lab.lab1.test_clientserver")

class TestClientServer(unittest.TestCase):

    _server = clientserver.Server()
    _server_thread = threading.Thread(target=_server.serve)

    @classmethod
    def setUpClass(cls):
        logger.info("Setting up class: starting server thread...")
        cls._server_thread.start()
        time.sleep(1)

    def setUp(self):
        logger.info("Setting up test: creating new client...")
        self.client = clientserver.Client()

    def test_get_existing_entry(self):
        logger.info("Running test: GET existing entry (Alice)")
        response = self.client.call("GET Alice")
        logger.info(f"Response received: {response}")
        self.assertEqual(response, "1234")

    def test_getall_entries(self):
        logger.info("Running test: GETALL all entries")
        response = self.client.call("GETALL")
        logger.info(f"Response received: {response}")
        expected = str({"Alice": "1234", "Bob": "5678", "Charlie": "9012"})
        self.assertEqual(response, expected)

    def test_invalid_command(self):
        logger.info("Running test: INVALID command")
        response = self.client.call("HELLO")
        logger.info(f"Response received: {response}")
        self.assertEqual(response, "INVALID REQUEST")

    def tearDown(self):
        logger.info("Tearing down test: closing client...")
        self.client.close()

    @classmethod
    def tearDownClass(cls):
        logger.info("Tearing down class: stopping server...")
        cls._server._serving = False
        cls._server_thread.join()
        logger.info("Server stopped.")

if __name__ == '__main__':
    unittest.main()
