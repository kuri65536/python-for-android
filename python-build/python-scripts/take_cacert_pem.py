import sys
import os


if sys.version_info[0] == 2:
    from urllib import urlretrieve
else:
    from urllib.request import urlretrieve


def main():
    fname = os.path.dirname(__file__)
    fname = os.path.join(fname, "cacert.pem")
    if os.path.exists(fname):
        return fname
    urlretrieve("http://curl.haxx.se/ca/cacert.pem", fname)
    return fname


if __name__ == "__main__":
    main()
