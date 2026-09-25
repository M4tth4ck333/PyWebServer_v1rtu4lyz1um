# Import socket module
import socket
import datetime
import os

# Create a TCP server socket (IPv4, TCP)
listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Assign port and host
PORT = 8080
HOST = ''

# Create a log
log = open('log.txt', 'a')
log.write("Python Web Server Log \n")

# Bind and listen
listener.bind((HOST, PORT))
listener.listen(1)

print(f"Running on port: {PORT}")
log.write(f"Running on port: {PORT}\n")

try:
    while True:
        print('Ready to serve...')
        log.write("\nReady to serve...\n")
        
        connection, addr = listener.accept()
        try:
            request = connection.recv(1024).decode('utf-8')
            log.write(f"HTTP Request:\n {request} \n")
            log.write(f"Time: {datetime.datetime.today()}\n")
            
            req = request.split()
            path = "index.html" # Default fallback
            if len(req) > 1:
                path = req[1][1:] # Strip leading '/'
                if path == "":
                    path = "index.html"
            
            log.write(f"Url Path: {path}\n")
            
            # Check if file exists to prevent hard crashes
            if os.path.exists(path) and os.path.isfile(path):
                with open(path, "rb") as f:
                    content = f.read()
                
                connection.send(b'HTTP/1.0 200 OK\r\n')
                log.write("Send HTTP 200 OK\n")
                connection.send(b"Content-type: text/html; charset=utf-8\r\n\r\n")
                connection.send(content)
            else:
                raise IOError(f"File not found: {path}")

            connection.close()
            log.write("Connection close\n")

        except Exception as e:
            # Send HTTP response message for file not found / error
            error_body = f"<h1>404 Not Found</h1><br/>File not found or error: {path}".encode('utf-8')
            connection.send(b'HTTP/1.0 404 Not Found\r\n')
            log.write("Send HTTP 404 Not Found\n")
            connection.send(b"Content-type: text/html; charset=utf-8\r\n\r\n")
            connection.send(error_body)
            connection.close()
            log.write(f"Connection close (Error: {e})\n")

finally:
    listener.close()
    log.write("Listener close\n")
    log.close()
