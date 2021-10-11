from functools import partial
import roles.gamestation.p3_roc
import queue
import time
import threading

class Multimorphic(threading.Thread):
    def __init__(self, callback):
        threading.Thread.__init__(self)
        self.callback = callback
        self.p3 = p3_roc.P3Jab()
        self.switches = {
            "derecha":"A0-B0-4",
            "dinero":"A0-B0-3",
            "izquierda":"A0-B0-0",
            "kicker":"A0-B0-2",
            "pop_left":"A0-B1-0",
            "pop_middle":"A0-B1-1",
            "pop_right":"A0-B1-2",
            "sling_left":"A0-B1-5",
            "sling_right":"A0-B1-4",
            "trueque":"A0-B0-1",
        }
        self.coils = {
            "derecha_hold":"A0-B1-3",
            "derecha_main":"A0-B1-2",
            "dinero":"A0-B0-6",
            "izquierda_hold":"A0-B1-1",
            "izquierda_main":"A0-B1-0",
            "kicker":"A0-B0-0",
            "pop_left":"A0-B0-2",
            "pop_middle":"A0-B0-3",
            "pop_right":"A0-B0-4",
            "sling_left":"A0-B1-4",
            "sling_right":"A0-B1-5",
            "trueque":"A0-B0-1",
        }
        self.queue = queue.Queue()
        # switches
        self.p3.configure_switch_callback(self.switches["dinero"], self.dinero_handler)
        self.p3.configure_switch_callback(self.switches["kicker"], self.kicker_handler)
        self.p3.configure_switch_callback(self.switches["pop_left"], self.pop_left_handler)
        self.p3.configure_switch_callback(self.switches["pop_middle"], self.pop_middle_handler)
        self.p3.configure_switch_callback(self.switches["pop_right"], self.pop_right_handler)
        self.p3.configure_switch_callback(self.switches["sling_left"], self.sling_left_handler)
        self.p3.configure_switch_callback(self.switches["sling_right"], self.sling_right_handler)
        self.p3.configure_switch_callback(self.switches["trueque"], self.trueque_handler)
        # configure autofire
        self.p3.configure_pops_slings(self.switches["pop_left"], self.coils["pop_left"], 50)
        self.p3.configure_pops_slings(self.switches["pop_middle"], self.coils["pop_middle"], 50)
        self.p3.configure_pops_slings(self.switches["pop_right"], self.coils["pop_right"], 50)
        self.p3.configure_pops_slings(self.switches["sling_left"], self.coils["sling_left"], 10)
        self.p3.configure_pops_slings(self.switches["sling_right"], self.coils["sling_right"], 10)
        self.start()

    def _enable_gameplay(self):
        self.p3.configure_flipper(self.switches["izquierda"], self.coils["izquierda_main"], self.coils["derecha_hold"], 25)
        self.p3.configure_flipper(self.switches["derecha"], self.coils["derecha_main"], self.coils["derecha_hold"], 20)
        self.p3.configure_pops_slings(self.switches["kicker"], self.coils["kicker"], 25)

    def _disable_gameplay(self):
        self.p3.clear_rule(self.switches["izquierda"])
        self.p3.clear_rule(self.switches["derecha"])
        self.p3.clear_rule(self.switches["kicker"])
        self.p3.disable_coil(self.coils["izquierda_hold"])
        self.p3.disable_coil(self.coils["derecha_hold"])
    def _pulse_coil(self,coil_name, duration_ms):
        if duration_ms < 50: #safety limit
            self.p3.pulse_coil(self.coils[coil_name], duration_ms)

    def izquierda_handler(self,event_state):
        self.callback("event_button_izquierda",event_state, "multimorphic", None)
    def trueque_handler(self,event_state):
        self.callback("event_button_trueque",event_state, "multimorphic", None)
    def kicker_handler(self,event_state):
        self.callback("event_button_comienza",event_state, "multimorphic", None)
    def dinero_handler(self,event_state):
        self.callback("event_button_dinero",event_state, "multimorphic", None)
    def derecha_handler(self,event_state):
        self.callback("event_button_derecha",event_state, "multimorphic", None)
    def pop_left_handler(self,event_state):
        self.callback("event_pop_left",event_state, "multimorphic", None)
    def pop_middle_handler(self,event_state):
        self.callback("event_pop_middle",event_state, "multimorphic", None)
    def pop_right_handler(self,event_state):
        self.callback("event_pop_right",event_state, "multimorphic", None)
    def sling_left_handler(self,event_state):
        self.callback("event_slingshot_left",event_state, "multimorphic", None)
    def sling_right_handler(self,event_state):
        self.callback("event_slingshot_right",event_state, "multimorphic", None)

    def enable_gameplay(self):
        self.add_to_queue("event_enable_gameplay")
    def disable_gameplay(self):
        self.add_to_queue("disable_gameplay")
    def pulse_coil(self,coil_name, duration_ms):
        self.add_to_queue("pulse_coil",[coil_name, duration_ms])
    def add_to_queue(self, command, params=[]):
        self.queue.put((command, params))

    def run(self):
        while True:
            try:
                command, params = self.queue.get(True,0.01)
                if command == "enable_gameplay":
                    self._enable_gameplay()
                if command == "disable_gameplay":
                    self._disable_gameplay()
                if command == "pulse_coil":
                    self._pulse_coil(params[0],params[1])
            except queue.Empty:
                self.p3.poll()


"""
def test_callback(event_name,event_state):
    print(event_name,event_state)

multimorphic = Multimorphic(test_callback)

multimorphic.pulse_coil("kicker", 25)

multimorphic.enable_gameplay()
"""
