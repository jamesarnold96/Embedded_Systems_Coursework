# -*- coding: utf-8 -*-
"""
Created on Wed Feb  7 20:25:02 2018

@author: james
"""

#!C:\Users\james\Documents\Python\WinPython-64bit-3.6.3.0Qt5\python-3.6.3.amd64\python.exe

import cgi
import cgitb
cgitb.enable(display=0, logdir="C:\xampp\htdocs\testing\logdir")

def htmlTop():
    print("""Content-type:text/html\n\n
          <!DOCTYPE html>
          <html lang = "en">
          <head>
          <meta charset = "utf-8"/>
          <title>My server-side template</title>
          <body>""")
    
def htmlTail():
    print("""</body>
          </html>""")
    
def getData():
    formData = cgi.FieldStorage()
    buttonState = formData.getvalue('buttonState')
    return buttonState
    
# main program
if __name__ == "__main__":
    try:
        htmlTop()
        buttonState = getData()
        if buttonState == "true": # JS true != Python True
           print("Connection Successful!")
        htmlTail()
    except:
        cgi.print_exception()