#!C:\Users\james\Documents\Python\WinPython-64bit-3.6.3.0Qt5\python-3.6.3.amd64\python.exe

import cgi

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
    firstname = formData.getvalue('firstname')
    return firstname
    
# main program
if __name__ == "__main__":
    try:
        htmlTop()
        firstName = getData()
        print("Hello {0}!".format(firstName))
        htmlTail()
    except:
        cgi.print_exception()