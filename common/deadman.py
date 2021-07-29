import threading
import queue

class Safety_Enable(threading.Thread):
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
                self.tb.publish("deadman", error_message)
                break
            except queue.Empty:    
                self.tb.publish("deadman", "safe")
            time.sleep(1)
