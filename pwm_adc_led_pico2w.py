from machine import Pin, PWM, ADC
import time
import network
import socket

def ap_setup():
    ap = network.WLAN(network.WLAN.IF_AP)
    ap.config(ssid = 'pico' , password = 'nahuh123_123')
    ap.active(True)
    
    print("IP : " , ap.ifconfig()[0])
    
def setup_socket():
    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(3)
    
    return s
    
def web_page(brightness, temperature):
    html_page = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Control LED Brightness</title>
        </head>
        <body style="margin:0; display:flex; flex-direction:column; justify-content:center; align-items:center; height:100vh; font-family:Arial; background-color:#f0f0f0;">
            
            <h1 style="margin:20px; color:#333;">LED Brightness Control</h1>
            <h3 style="margin:10px; color:#666;">Temperature: {temperature}C</h3>

            <div style="background-color:white; padding:30px; border-radius:12px; box-shadow:0 4px 6px rgba(0,0,0,0.1); text-align:center; min-width:300px;">
                
                <p style="font-size:20px; margin:15px 0; color:#333;">
                    Brightness: <strong id="brightnessValue">{brightness}%</strong>
                </p>

                <input type="range" id="brightnessSlider" min="0" max="100" value="{brightness}"
                    style="width:100%; height:8px; border-radius:5px; background:#ddd; outline:none; cursor:pointer; margin:20px 0;">
                
                <p style="font-size:14px; color:#888; margin-top:10px;">
                    Drag slider to adjust brightness
                </p>

            </div>

            <script>
                const slider = document.getElementById('brightnessSlider');
                const valueDisplay = document.getElementById('brightnessValue');
                
                slider.addEventListener('input', function() {{
                    valueDisplay.textContent = this.value + '%';
                }});
                
                slider.addEventListener('change', function() {{
                    fetch('/brightness?value=' + this.value)
                        .then(response => response.text())
                        .then(data => console.log('Brightness updated'))
                        .catch(error => console.error('Error:', error));
                }});
            </script>

        </body>
        </html>
    """
    return str(html_page)

def get_temp(sensor_temp):
    conversion_factor = 3.3 / (65535)
    reading = sensor_temp.read_u16() * conversion_factor
    temperature = 27 - (reading - 0.706)/0.001721
    return temperature

ap_setup()
s = setup_socket()
pwm = PWM(Pin(15), freq=1000)
sensor_temp = ADC(4)
temprature = 0.0
brightness = 0.0

try:
    while True:
        
        client = s.accept()[0]
        req = client.recv(1024)
        
        req = str(req).split()[1]
        
        temprature = get_temp(sensor_temp)
        
        try:
            path = req.split('?')[0]
            
            if path == '/brightness':
                value = int(req.split('=')[1])
                brightness = value * 655
                pwm.duty_u16(brightness)
        except:
            print()
            
        client.send('HTTP/1.1 200 OK\r\nContent-type: text/html\r\n\r\n')
        client.send(web_page(brightness, temprature))
        
        client.close()
        
except:
    print("End")