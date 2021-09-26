#!/usr/bin/python3
__version__ = "1.0.1"

DEBUG = False



################################ REMOTE USE ################################
#
# Remote parameters
#   /shutdown - shutdown the device
#   /test     - connection test
#
# Use curl or your favorite browser
#  curl http://<device IP or hostname>:port/[param] 
#
############################################################################



from http.server import BaseHTTPRequestHandler, HTTPServer
from optparse import OptionParser
import os, platform

###################################################################################################

def is_rasPi():
    if DEBUG:
        return True

    if platform.system() == "Windows":
        return False
    else:
        ret = os.uname().machine.lower().rfind("armv")
        return True if ret != -1 else False

###################################################################################################

def is_root():
    return os.geteuid() == 0

###################################################################################################
###################################################################################################

class MyHTTPServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        html_text = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ShutdownServer</title>
</head>
<body>
    <section style = "text-align: center;">
        {'<strong>KO</strong>' if self.path != "/test" and self.path != "/shutdown" else ''}
        {'<strong>OK</strong>' if self.path == "/test" else ''}
        {'<strong>OK, Bye</strong>' if self.path == "/shutdown" else ''}
        {'<br/>' if self.path == "/shutdown" and is_rasPi() else ''}
        {'<br/>' if self.path == "/shutdown" and is_rasPi() else ''}
        {'<strong>After a while, unplug the power adapter from the wall!!</strong>' if self.path == "/shutdown" and is_rasPi() else ''}
    </section>
</body>
</html>

"""

        user_agent = self.headers.get("User-Agent").split('/')[0]      # curl, wget, Mozilla, Chrome

        if user_agent.lower() in ["curl", "wget"]:
            if self.path == "/shutdown":
                self.wfile.write(b'OK, Bye.\n')
                if is_rasPi():
                    self.wfile.write(b'After a while, unplug the power adapter from the wall!!\n')
                self.wfile.write(b'\r')

            elif self.path == "/test":
                self.wfile.write(b'OK\n\r')
            else:
                self.wfile.write(b'KO\n\r')
        else:
            self.wfile.write(bytes(html_text, 'utf-8'))


        if self.path == "/shutdown":
            os.popen("sudo shutdown now") if DEBUG != True else print("Shutting Down")

###################################################################################################
###################################################################################################

def httpMethod(httpServerPort):

    if platform.system() == "Windows":
        httpHostName = platform.uname().node
    else:
        httpHostName = os.uname()[1]
    httpHostName += ".local"

    webServer = HTTPServer((httpHostName, httpServerPort), MyHTTPServer)

    print("ShutdownServer started:")
    port = f":{httpServerPort if httpServerPort != 80 else ''}"
    print(f"\thttp://{httpHostName}{port}")

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("ShutdownServer stopped.")

###################################################################################################

def main():
    httpServerPort = 80

    parser = OptionParser(usage = "ShutdownServer -p <port number>")
    parser.add_option("-p", "--port", dest = "port", type = "int", help = "Port number, default = 80")

    (options, _) = parser.parse_args()
    if options.port != None:
        httpServerPort = options.port

    httpMethod(httpServerPort)

###################################################################################################
###################################################################################################

if __name__ == "__main__":
    if is_root():
        main()
    else:
        print("[ERROR] This script must be run as ROOT or with SUDO privileges!")
        
