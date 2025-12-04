import network
import time
import socket
from machine import Pin

def ap_setup():
    ap = network.WLAN(network.WLAN.IF_AP)
    ap.config(ssid = 'pico' , password = 'nahuh123_123')
    ap.active(True)

    print("Connected IP : ", ap.ifconfig()[0])
    
def open_socket():
    address = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(address)
    s.listen(3)
    
    return s

def web_page():
    html_page = """
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Control led</title>
                </head>
                <body>
                    <h1>Hello World</h1>
                    <form action='./on'>
                        <input type='submit' value='ON'></input>
                    </form>
                    <form action='./off'>
                        <input type='submit' value='OFF'></input>
                    </form>
                </body>
                </html>
                """
    return str(html_page)
    
def req_to_on_off(req):
    
    req = req.split('?')[0]
    if req == "b'GET /on":
        return 1
    else:
        return 0
    
# ---------------------------------------------------------------------------------------------- main prog

led = Pin("LED", Pin.OUT)
led.value(0)

ap_setup()
s = open_socket()

try:
    while True:
        client = s.accept()[0]
        req = client.recv(1024)
        led.value(req_to_on_off(str(req)))

        html = web_page()
        client.send('HTTP/1.1 200 OK\r\nContent-type: text/html\r\n\r\n')
        client.send(html)
        client.close()
except:
    s.close()
    print("Connections closed")