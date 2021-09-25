#!/usr/bin/python3
__version__ = "1.0.0"


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
###################################################################################################

class MyHTTPServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        if self.path == "/shutdown":
            self.wfile.write(b"OK, Bye")
            os.popen("sudo shutdown now")

        if self.path == "/test":
            self.wfile.write(b"OK")
        else:
            self.wfile.write(b"KO")

###################################################################################################
###################################################################################################

def httpMethod(httpServerPort):

    if platform.system() == "Windows":
        httpHostName = platform.uname().node
    else:
        httpHostName = os.uname()[1]
    httpHostName += ".local"

    webServer = HTTPServer((httpHostName, httpServerPort), MyHTTPServer)

    print("[INFO] ShutdownServer started:")
    port = f":{httpServerPort if httpServerPort != 80 else ''}"
    print(f"\thttp://{httpHostName}{port}")

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("[INFO] ShutdownServer stopped.")

###################################################################################################

def is_root():
    return os.geteuid() == 0

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
        
