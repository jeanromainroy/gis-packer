"""
    HTTP Server
"""

import os
from http.server import SimpleHTTPRequestHandler
import socketserver

def launch(dir_path, HOST='0.0.0.0', PORT=8888):
    """Module to launch a simple http server exposing an arbitrary directory

    Arguments
    ----------
        dir_path : str
            Path to the directory that will be exposed
    """

    # validate input
    if not os.path.abspath(dir_path):
        raise Exception('Must be an absolute path')

    if not os.path.isdir(dir_path):
        raise Exception('Directory does not exist')

    # change working directory
    os.chdir(dir_path)

    # init server
    with socketserver.TCPServer((HOST, PORT), SimpleHTTPRequestHandler) as server:
        print(f"serving at http://{HOST}:{PORT}, (ctrl+c to exit)")
        server.serve_forever()
