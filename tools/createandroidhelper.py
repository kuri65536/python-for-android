#-------------------------------------------------------------------------------
# Name:     createandroidhelper.py
#
# Purpose:  To automagically generate androidhelper.py file containing a
#           "helper" class to simplify Python-for-Android SL4A development
#           in IDEs environments
#
# Known Issues:
# 1. viewMap(self,query) wiki for some reason copies example string - need to manually correct
# 2. def dialogCreateSeekBar(self,starting_value=50,maximum_value=100,title="",message=""): problem with title & message being non-default values
#
#
# Usage:
# Before running this program, download and unzip SL4A API documentation
# HTML files contained in the following zip file to a local folder:
# http://android-scripting.googlecode.com/hg/android/ScriptingLayerForAndroid/assets/sl4adoc.zip
#
# Then run the program as follows:
#
# python createandroidhelper.py <HTML FILES DIR> <androidhelper.py TARGET DIR>
#
# <HTML FILES DIR> = The local folder where the zip file has been unzipped

# <androidhelper.py TARGET DIR> = In which folder do you want androidhelper.py
# to be generated. if this is missing or unreachable the program will try to
# generate the file in the folder where createandroidhelper.py is located
#
# Version:  0.1 alpha, created on 7-Apr-2012
#
# Author:   Hariharan Srinath (srinathdevelopment@gmail.com)
#
# Copyright:    Copyright (C) 2012, Hariharan Srinath
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.
#-------------------------------------------------------------------------------
#!/usr/bin/env python

usagestring = """Name:     createandroidhelper.py
Purpose:  To automagically generate androidhelper.py file containing a
          "helper" class to simplify Python-for-Android SL4A development
          in IDEs environments
Usage:
Before running this program, download and unzip SL4A API documentation
HTML files contained in the following zip file to a local folder:
http://android-scripting.googlecode.com/hg/android/ScriptingLayerForAndroid/assets/sl4adoc.zip

Then run the program from shell as follows:

python createandroidhelper.py <HTML FILES DIR> <androidhelper.py TARGET DIR>

<HTML FILES DIR> = The local folder where the zip file has been unzipped

<androidhelper.py TARGET DIR> = In which folder do you want androidhelper.py
to be generated. if this is missing or unreachable the program will try to
generate the file in the folder where createandroidhelper.py is located"""

startstring = """#-------------------------------------------------------------------------------
# Name:         androidhelper.py
#
# Purpose:      To simplify Python-for-Android SL4A development in IDEs with a
#               "hepler" class derived from the default Android class containing
#               SL4A facade functions & API documentation
#
# Usage:        copy androidhelper.py into either the folder containing your
#               SL4A python script or to some location on the python import path
#               that your IDE can see and in your script, instead of:
#
#                   import android
#
#               use the following import code:
#
#                   try:
#                       import androidhelper as android
#                   except:
#                       import android
#
# Sources:      Derived from API documentation in HTML files contained in
#               /android-scripting/android/ScriptingLayerForAndroid/assets/sl4adoc.zip
#
# Version:      for SL4A Release R5, created on 7-Apr-2012
#
# Author(s):    Hariharan Srinath (srinathdevelopment@gmail.com) with inputs
#               from Robert J Matthews (rjmatthews62@gmail.com)
#
# Copyright:    Copyright (C) 2012, Hariharan Srinath, Robert J Matthews
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

import android

class Android(android.Android):"""


from bs4 import BeautifulSoup
import os.path
import sys

def main():
    try:
        basedocdir = sys.argv[1]
        infile = open(os.path.join(basedocdir,"index.html"),"r")
    except IndexError:
        print "ERROR: You MUST specify <HTML FILES DIR> as first argument"
        print usagestring
        exit(-1)
    except IOError:
        print "ERROR: Could not find index.html in "+basedocdir
        print usagestring
        exit(-1)

    try:
        andhelperfildir = sys.argv[2]
        outpath =os.path.join(andhelperfildir,"androidhelper.py")
        print "Found index.html. Trying to create "+outpath
        outfile = open(outpath,"w")
    except IndexError,IOError:
        altpath =os.path.join(os.path.dirname(sys.argv[0]),"androidhelper.py")
        print "ERROR: <androidhelper.py TARGET DIR> was not found or failed to create androidhelper.py there"
        print "Trying to create "+altpath+" instead"
        try:
            outfile = open(altpath,"w")
        except IOError:
            print "ERROR: Failed!"
            print usagestring
            exit(-1)

    idxsoup = BeautifulSoup(infile.read())
    infile.close()

    print "starting to write androidhelper.py"
    outfile.write( startstring)
    outfile.write("\n")

    for facade in idxsoup.findAll("a"):
        print "processing "+facade["href"]
        html = open(os.path.join(basedocdir,facade["href"]),"r").read()
        html = html.replace("<br>","")
        html = html.replace("<BR>","")
        optionalstring ="(optional)"
        defaultstring = "(default="

        soup = BeautifulSoup(html)
        apifunctions =[]

        #each table row is a API Function
        for row in soup.table.findAll("tr"):
            #each API function name is contained in the <a> tag parameter "name"
            func_name = row.find("a")["name"].strip()

            #rest of the description is in the second table cell - both parameter info & documenatation
            func_docstuff = row.findAll("td")[1]

            func_parameters = []

            #each parameter name, with the notable exception of "Example" is bolded - ie. <b>title (String)</b>  (optional)
            for eachb in func_docstuff.findAll("b"):
                #the first word is the parameter name
                paramname = eachb.text[:eachb.text.find("(")].strip()
                #skip if the bold text is "Example"
                if(paramname == "Example" or paramname=="returns:"):
                    continue

                #the second word is the type of variable - this is necessary in case of default values or optional
                paramtype = eachb.text[eachb.text.find("(")+1:eachb.text.find(")")].strip()

                #now, try to identify whether the variable is optional or possibly has a default value
                parammod = None

                #func_docstuff.contents has a list of items, some of which are the <b> tags which form the parameter names
                #we check to see whether the next list item corresponding to this parameter has either (optional) or (default=
                for ctr in range(len(func_docstuff.contents)):
                    if((func_docstuff.contents[ctr]==eachb) and (ctr+1)<len(func_docstuff.contents)):
                        checkitem =func_docstuff.contents[ctr+1]
                        if(checkitem.find(optionalstring)>-1):
                            parammod = ["Optional",None]
                        elif(checkitem.find(defaultstring)>-1):
                            stpos = checkitem.find(defaultstring)+len(defaultstring)
                            endpos = checkitem.find(")",stpos)
                            defitem = checkitem[stpos:endpos]
                            parammod = ["Default",defitem]
                        else:
                            parammod = ["Required",None]

                        break

                if(parammod == None):
                    print "error: Parameter info not found for "+paramname
                    exit(-1)
                else:
                    paramname = paramname.replace(" ","_")
                    func_parameters.append({"paramname":paramname, "paramtype":paramtype,"parammod":parammod})

            apifunctions.append({"func_name":func_name, "func_parameters":func_parameters, "func_docstuff":func_docstuff.text })

        for apifunction in apifunctions:
            functionstring ='\tdef '+apifunction["func_name"]+'(self,'
            rpcstring = '\t\treturn self._rpc("'+apifunction["func_name"]+'",'

            if( len (apifunction["func_parameters"])>0):
                for parameter in apifunction["func_parameters"]:
                    functionstring = functionstring+parameter["paramname"]
                    rpcstring = rpcstring + parameter["paramname"]

                    if(parameter["parammod"][0]=="Optional"):
                        functionstring = functionstring + "=" + "None"
                    elif(parameter["parammod"][0]=="Default"):
                        functionstring = functionstring + "="

                        if(parameter["paramtype"]=="String"):
                            parameter["parammod"][1]='"'+parameter["parammod"][1]+'"'
                        elif(parameter["paramtype"]=="Boolean"):
                            if(parameter["parammod"][1].lower()=="false"):
                                parameter["parammod"][1]="False"
                            elif(parameter["parammod"][1].lower()=="true"):
                                parameter["parammod"][1]="True"

                        functionstring = functionstring +parameter["parammod"][1]

                    functionstring = functionstring + ","
                    rpcstring = rpcstring + ","

            #drop the trailing commas
            functionstring = functionstring[:-1]
            rpcstring = rpcstring[:-1]

            functionstring = functionstring + "):"
            rpcstring = rpcstring+")"
            apidoctext = "\t\t'''\n"
            apidoctext = apidoctext+"\t\t"+functionstring[5:-1].replace("self,","")+"\n"

            doclinectr = 0

            for txtline in apifunction["func_docstuff"].replace("\r","").split("\n"):
                txtline = txtline.strip()
                if(txtline!=""):
                    if(doclinectr>0 and doclinectr<len(apifunction["func_parameters"])+1):
                        apidoctext=apidoctext+ "\t\t\t"+txtline+"\n"
                    else:
                        apidoctext = apidoctext + "\t\t"+txtline+"\n"

                    doclinectr = doclinectr+1

            apidoctext = apidoctext+"\t\t'''"
            print "\twriting "+functionstring[5:]
            outfile.write(functionstring)
            outfile.write("\n")
            outfile.write(apidoctext)
            outfile.write("\n")
            outfile.write(rpcstring)
            outfile.write("\n\n")

    outfile.close()

if __name__ == '__main__':
    main()
