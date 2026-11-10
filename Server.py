import os
import json
import time
import threading
import socket
import datetime
import cherrypy
from cheroot import wsgi
from pyboy import PyBoy

SYSTEM_DLC_MANIFEST = "2fe9fc84431b4369d35cfdb3482920ebe7de1375"

# --- 1. PyBoy Cheroot Background Node ---
class IPyPyCherootServer:
    def __init__(self, rom_path: str, host: str = "127.0.0.1", port: int = 8081):
        self.host = host
        self.port = port
        self.dlc = SYSTEM_DLC_MANIFEST
        # Fallback wenn ROM nicht existiert, aber strukturell bereit
        try:
            self.pyboy = PyBoy(rom_path, window="null")
            self.has_rom = True
        except Exception:
            self.pyboy = None
            self.has_rom = False
            
        self.server = None
        self.thread = None

    def wsgi_app(self, environ, start_response):
        path = environ.get('PATH_INFO', '')
        
        if path == '/api/status':
            if self.has_rom and self.pyboy:
                self.pyboy.tick()
                cart_title = self.pyboy.cartridge_title
            else:
                cart_title = "MOCK_TCG_CARTRIDGE"

            data = {
                "status": "running",
                "engine": "ipypy3 + cheroot",
                "dlc_guard": self.dlc,
                "cartridge": cart_title
            }
            body = json.dumps(data).encode('utf-8')
            start_response('200 OK', [('Content-Type', 'application/json'), ('Access-Control-Allow-Origin', '*')])
            return [body]
            
        start_response('404 Not Found', [('Content-Type', 'text/plain')])
        return [b'Not Found']

    def start_background(self):
        self.server = wsgi.Server((self.host, self.port), self.wsgi_app)
        self.thread = threading.Thread(target=self.server.start, daemon=True)
        self.thread.start()
        print(f"[ipypy3] Cheroot Emulation Bridge aktiv auf http://{self.host}:{self.port}")

    def stop(self):
        if self.server:
            self.server.stop()
            if self.has_rom and self.pyboy:
                self.pyboy.stop()
            print("[ipypy3] Cheroot Server gestoppt.")

# --- 2. CherryPy Main Gateway für v1rtu4lyz1um.com ---
class V1rtu4lyz1umServer:
    def __init__(self):
        self.dlc = SYSTEM_DLC_MANIFEST
        self.state = {
            "domain": "v1rtu4lyz1um.com",
            "dlc_guard": self.dlc,
            "status": "active",
            "architecture": "SystemTUV Overlay Hypervisor"
        }

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def index(self):
        cherrypy.response.headers['Access-Control-Allow-Origin'] = '*'
        return {
            "message": "SystemTUV & PyWebServer_v1rtu4lyz1um online.",
            "dlc_manifest": self.dlc,
            "endpoints": ["/api/state", "/api/frame"]
        }

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def api_state(self):
        cherrypy.response.headers['Access-Control-Allow-Origin'] = '*'
        return self.state

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def api_frame(self):
        cherrypy.response.headers['Access-Control-Allow-Origin'] = '*'
        return {
            "dlc_guard": self.dlc,
            "timestamp": time.time_ns(),
            "canvas_commands": [
                {"op": "clear", "color": "#0f380f"},
                {"op": "text", "x": 10, "y": 20, "text": "v1rtu4lyz1um TCG Core", "color": "#8bac0f"}
            ]
        }

if __name__ == "__main__":
    print(f"[SystemTUV] Initialisiere v1rtu4lyz1um Stack unter DLC: {SYSTEM_DLC_MANIFEST}")
    
    # Start des PyBoy/Cheroot-Subsystems im Hintergrund (Port 8081)
    emulator_bridge = IPyPyCherootServer("game.gb", host="127.0.0.1", port=8081)
    emulator_bridge.start_background()

    # Start des Haupt-CherryPy-Gateways (Port 8080)
    conf = {
        '/': {
            'tools.sessions.on': True,
            'tools.response_headers.on': True,
            'tools.response_headers.headers': [('Server', 'PyWebServer_v1rtu4lyz1um')]
        }
    }
    
    cherrypy.config.update({
        'server.socket_host': '0.0.0.0',
        'server.socket_port': 8080
    })
    
    print("[v1rtu4lyz1um] Haupt-Webserver startet auf Port 8080...")
    try:
        cherrypy.quickstart(V1rtu4lyz1umServer(), '/', conf)
    finally:
        emulator_bridge.stop()
