from __future__ import print_function
import sys
try:
    import setuptools
    setuptools              # supress lint error.
except:
    print("setuptools is needed to make egg.\n"
          "download ez_setup and try to run:\n"
          "  $ %s -c \"from urllib import urlretrieve as u; "
          "u('http://peak.telecommunity.com/dist/ez_setup.py', "
          "'ez_setup.py')\"\n"
          "  $ %s ez_setup.py setuptools")
    sys.exit(1)

# vi: ft=python:et:ts=4:fdm=marker
# one liner for download ez_setup
# python -c "import urllib2; r=urllib2.urlopen(url);
#            file('ez_setup.py', 'w').write(r.read())"
# python -c "from urllib import urlretrieve as u; u(url, 'ez_setup.py')"
