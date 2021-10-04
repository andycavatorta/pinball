from typing import Dict
import pinproc
import string

class P3Jab:

    """Minimal shim for using the P3-Roc."""

    def __init__(self):
        """Initialize platform."""
        self.proc = pinproc.PinPROC(pinproc.normalize_machine_type('pdb'))
        self.proc.reset(1)
        self.callbacks = {}     # type: Dict[str:callable]

    def get_switch_states(self):
        """Get initial switch states."""
        return self.proc.switch_get_states()

    @staticmethod
    def _parse_coil_number(number_str: str):
        board_num, bank_num, coil_num = number_str.split("-", 2)
        #return board_num * 16 + bank_num * 8 + coil_num
        return int(board_num.strip(string.ascii_letters)) * 16 + int(bank_num.strip(string.ascii_letters)) * 8 + int(coil_num.strip(string.ascii_letters))

    def pulse_coil(self, number_str: str, pulse_ms: int):
        """Pulse coil for pulse_ms."""
        self.proc.driver_pulse(self._parse_coil_number(number_str), pulse_ms)

    @staticmethod
    def _parse_switch_number(number_str: str):
        board_num, bank_num, switch_num = number_str.split("-", 2)
        return int(board_num.strip(string.ascii_letters)) * 16 + int(bank_num.strip(string.ascii_letters)) * 8 + int(switch_num.strip(string.ascii_letters))

    def configure_switch_callback(self, number_str: str, callback: callable):
        """Configure callback for switch on change."""
        switch_num = self._parse_switch_number(number_str)
        self.proc.switch_update_rule(switch_num, 'closed_debounced', {'notifyHost': True, 'reloadActive': False}, [], False)
        self.proc.switch_update_rule(switch_num, 'open_debounced', {'notifyHost': True, 'reloadActive': False}, [], False)
        self.callbacks[switch_num] = callback

    def configure_flipper(self, switch_number_str: str, coil_main_number_str: str, coil_hold_number_str: str, pulse_ms: int):
        """Configure flippers."""
        switch_number = self._parse_switch_number(switch_number_str)
        coil_main_number = self._parse_coil_number(coil_main_number_str)
        coil_hold_number = self._parse_coil_number(coil_hold_number_str)
        rules = [pinproc.driver_state_pulse(self.proc.driver_get_state(coil_main_number), pulse_ms),
                 pinproc.driver_state_pulse(self.proc.driver_get_state(coil_hold_number), 0)]
        self.proc.switch_update_rule(switch_number, "closed_nondebounced", {'notifyHost': False, 'reloadActive': False}, rules)

        rules = [pinproc.driver_state_disable(self.proc.driver_get_state(coil_hold_number))]
        self.proc.switch_update_rule(switch_number, "open_nondebounced", {'notifyHost': False, 'reloadActive': False}, rules)

    def configure_pops_slings(self, switch_number_str: str, coil_number_str: str, pulse_ms: int):
        """Configure pops or slings."""
        switch_number = self._parse_switch_number(switch_number_str)
        coil_number = self._parse_coil_number(coil_number_str)
        rules = [pinproc.driver_state_pulse(self.proc.driver_get_state(coil_number), pulse_ms)]
        self.proc.switch_update_rule(switch_number, "closed_nondebounced", {'notifyHost': False, 'reloadActive': False}, rules)
        self.proc.switch_update_rule(switch_number, "open_nondebounced", {'notifyHost': False, 'reloadActive': False}, [])

    def clear_rule(self, switch_number_str):
        """Clear rules on switch."""
        switch_number = self._parse_switch_number(switch_number_str)
        self.proc.switch_update_rule(switch_number, "closed_nondebounced", {'notifyHost': False, 'reloadActive': False}, [])
        self.proc.switch_update_rule(switch_number, "open_nondebounced", {'notifyHost': False, 'reloadActive': False}, [])

    def disable_coil(self, number_str):
        """Disable coil."""
        self.proc.driver_disable(self._parse_coil_number(number_str))

    def poll(self):
        """Poll for changes."""
        events = self.proc.get_events()
        self.proc.watchdog_tickle()
        self.proc.flush()
        for event in events:
            event_type = event['type']
            event_value = event['value']
            if event_type == pinproc.EventTypeSwitchClosedDebounced:
                if event_value in self.callbacks:
                    self.callbacks[event_value]("closed")
            elif event_type == pinproc.EventTypeSwitchOpenDebounced:
                if event_value in self.callbacks:
                    self.callbacks[event_value]("open")