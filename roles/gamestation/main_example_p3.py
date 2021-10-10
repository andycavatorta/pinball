# Usage example
import p3_jab
import time
from functools import partial


def test_callback(state):
    print("Switch A0-B0-3 is now state {}".format(state))


def enable_flippers(p3, state):
    if state:
        p3.configure_flipper("A0-B0-4", "A0-B1-2", "A0-B1-3", 20)


def disable_flippers(p3, state):
    if state:
        # clear rule and disable hold coil (it might be still active)
        p3.clear_rule("A0-B1-2")
        p3.disable_coil("A0-B1-3")


def main():
    import p3_jab
    p3 = p3_jab.P3Jab()

    p3.configure_switch_callback("A0-B0-3", test_callback)
    p3.configure_switch_callback("A0-B0-1", partial(enable_flippers, p3))
    p3.configure_switch_callback("A0-B0-2", partial(disable_flippers, p3))
    p3.pulse_coil("A0-B0-2", 40)

    p3.configure_pops_slings("A0-B1-5", "A0-B1-4", 30)

    # go into busy loop to poll changes from the P3-Roc
    while True:
        p3.poll()
        time.sleep(.005)


if __name__ == '__main__':
    main()