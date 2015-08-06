from __future__ import print_function, unicode_literals
import android
import time

skip_each = False
n_loop = 1
timeout = 3


# tests for python modification for android {{{1
def sensor(n):
    print("-" * 10 + "start %d sensor" % n + "-" * 10)
    droid = android.Android()
    ret = droid.startSensingTimed(n, 100)
    if ret.error:
        if "your OS version..." in ret.error:
            return True
        return False

    for i in range(n_loop):
        tn = tb = time.time()
        while tn - tb < timeout:
            events = droid.eventPoll(1).result
            tn = time.time()
            if events:
                break
            time.sleep(1)
        else:
            print("time out...")
            continue
        evsensor = []
        for ev in events:
            if ev["name"] != "sensors":
                continue
            evsensor.append(ev)
        if not evsensor:
            continue
        for ev in evsensor:
            print(time.time(), end="")
            print(":", end="")
            print(ev["data"])
    droid.stopSensing()
    return False


def main():
    sensor(1)
    if skip_each:
        return
    for i in range(2, 999):
        if sensor(i):
            break


if __name__ == '__main__':                                  # {{{1
    main()
# vi: ft=python:et:ts=4:fdm=marker
