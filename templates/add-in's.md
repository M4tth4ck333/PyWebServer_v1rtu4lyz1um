Add-in's.md
##             https://github.com/M4tth4ck333/pyodide-kernel
##             https://github.com/M4tth4ck333/kernel_gateway_demos.git
##             import xmlrpc.client
from cheroot import wsgi
from flask import Flask, jsonify, request

app = Flask(__name__)

# Verbindung zur Cobbler XML-RPC API (Standard-Port 25150)
COBBLER_SERVER = "http://127.0.0.1:25150/cobbler_api"


def get_cobbler_client():
  return xmlrpc.client.ServerProxy(COBBLER_SERVER, allow_none=True)


@app.route("/api/provision/system", methods=["POST"])
def trigger_cobbler_provision():
  data = request.get_json() or {}
  system_name = data.get("name", "test-vm-node")
  mac_address = data.get("mac", "52:54:00:12:34:56")
  profile = data.get("profile", "ubuntu-default")

  try:
    client = get_cobbler_client()
    # Token-Authentifizierung (Beispiel für Standard-Login)
    token = client.login("cobbler", "cobbler")

    # System-Objekt in Cobbler anlegen/aktualisieren
    system_id = client.new_system(token)
    client.modify_system(system_id, "name", system_name, token)
    client.modify_system(system_id, "image", profile, token)
    client.modify_system(
        system_id, "netboot_enabled", True, token
    )  # iPXE-Boot aktivieren
    client.save_system(system_id, token)

    # Cobbler-Konfiguration synchronisieren
    client.sync(token)

    return jsonify({
        "status": "success",
        "message": (
            f"System '{system_name}' mit MAC {mac_address} erfolgreich in"
            " Cobbler registriert."
        ),
    })
  except Exception as e:
    return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
  host = "127.0.0.1"
  port = 8080

  dispatcher = wsgi.PathInfoDispatcher({"/": app})
  server = wsgi.Server((host, port), dispatcher)

  print(
      f"[PyPy + Cheroot] Provisioning Gateway aktiv auf"
      f" http://{host}:{port}/api/provision/system"
  )
  try:
    server.start()
  except KeyboardInterrupt:
    server.stop()
#
