from __future__ import print_function, unicode_literals
import sys


# tests for python modification for android {{{1
def test_032s_wificonnect():                # issue sl4a #32 {{{1
    method = "WPA2"
    if method == "no-security":
        cfg = dict(
            SSID="invalidwifi",
            # below parameters are not used in example of my expalation site.
            # BSSID=,
            # hiddenSSID=False,
            # priority=,
            # apBand=,
        )
    elif method == "WEP":
        cfg = dict(
            SSID="invalidwifi",
            wepKeys=["key0"],
            wepTxKeyIndex=0,
        )
    else:   # elif method == "WPA2":
        cfg = dict(
            SSID="invalidwifi",
            password="testtesttest",
            # or you can use: presharedkey="0123456789ABCDEF...64B",
            # be careful SL4A can't allow 64byte key.
        )
    droid.wifiConnect(cfg)
    return True


if __name__ == '__main__':                                  # {{{1
    try:
        import android
    except:
        import os
        sys.path.insert(0, os.path.dirname(__file__))
        import android_mock as android      # for PC debugging
    droid = android.Android()

    test_032s_wificonnect()

# vi: ft=python:et:ts=4:fdm=marker
