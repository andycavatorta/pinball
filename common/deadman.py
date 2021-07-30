import threading
import queue

class Deadman_Switch(threading.Thread):
    def __init__(self, tb):
        threading.Thread.__init__(self)
        self.queue = queue.Queue()
        self.tb = tb
        self.start()

    def send_exception_and_stop(self, topic, error_message):
        self.queue.put(error_message)

    def run(self):
        while True:
            try:
                error_message = self.queue.get(False)
                print("deadman", error_message)
                self.tb.publish("deadman", error_message)
                break
            except queue.Empty:
                print("deadman", "safe")
                self.tb.publish("deadman", "safe")
            time.sleep(1)
