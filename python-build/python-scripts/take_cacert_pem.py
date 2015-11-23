import os
import urllib


def main():
    fname = "/mnt/sdcard/cacert.pem"
    if os.path.exists(fname):
        return False
    urllib.urlretrieve("http://curl.haxx.se/ca/cacert.pem", fname)
    return False


if __name__ == "__main__":
    main()
