import threading
import json
import datetime
from collections.abc import MutableMapping
from flask import Flask, render_template, jsonify, request
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from socketify import App
from cheroot import wsgi

# --- 1. Dunder-Overlay & JSONPath NodeGraph ---
Base = declarative_base()

class NodeGraphNode(MutableMapping):
    """Dunder-Overlay für JSONPath-Traversierung und direkte Schlüssel-Operationen."""
    def __init__(self, node_id: str, data: dict = None):
        self.id = node_id
        self._data = data if data is not None else {}

    @property
    def data(self):
        return self._data

    def __getitem__(self, key):
        if str(key).startswith("$"):
            return self._resolve_path(str(key))
        return self._data[key]

    def __setitem__(self, key, value):
        if str(key).startswith("$"):
            self._mutate_path(str(key), value)
        else:
            self._data[key] = value

    def __delitem__(self, key):
        del self._data[key]

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    def _resolve_path(self, path: str):
        if path == "$":
            return self._data
        clean_path = path[2:] if path.startswith("$.") else path[1:]
        current = self._data
        for part in clean_path.split("."):
            if not part:
                continue
            if "[" in part and part.endswith("]"):
                key, idx_str = part[:-1].split("[")
                current = current.get(key, [])[int(idx_str)]
            else:
                current = current[part]
        return current

    def _mutate_path(self, path: str, value):
        clean_path = path[2:] if path.startswith("$.") else path[1:]
        parts = clean_path.split(".")
        curr = self._data
        for part in parts[:-1]:
            curr = curr.setdefault(part, {})
        curr[parts[-1]] = value

# --- 2. SQLAlchemy Persistence ---
class SystemNodeRecord(Base):
    __tablename__ = 'system_node_records'
    id = Column(Integer, primary_key=True)
    node_id = Column(String, unique=True, nullable=False)
    payload = Column(Text)
    updated_at = Column(DateTime, default=datetime.datetime.now)

class DBManager:
    def __init__(self, db_path='v1rtu4lyz1um.db'):
        self.engine = create_engine(f'sqlite:///{db_path}')
        self.Session = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)

    def save_node(self, node: NodeGraphNode):
        session = self.Session()
        try:
            existing = session.query(SystemNodeRecord).filter_by(node_id=node.id).first()
            if existing:
                existing.payload = json.dumps(node.data)
                existing.updated_at = datetime.datetime.now()
            else:
                record = SystemNodeRecord(node_id=node.id, payload=json.dumps(node.data))
                session.add(record)
            session.commit()
        finally:
            session.close()

    def load_node(self, node_id: str) -> NodeGraphNode:
        session = self.Session()
        try:
            record = session.query(SystemNodeRecord).filter_by(node_id=node_id).first()
            if record:
                return NodeGraphNode(node_id, json.loads(record.payload))
            return None
        finally:
            session.close()

db = DBManager()

# --- 3. Flask App (Port 5000) ---
flask_app = Flask(__name__)

@flask_app.route('/')
def index():
    return render_template('index.html')

@flask_app.route('/api/status')
def flask_status():
    return jsonify({
        "status": "online",
        "game_mode": "AR-XAI-OpenWorld",
        "discovery": "Riemannian Manifold Exploration",
        "domain": "v1rtu4lyz1um.com"
    })

def run_flask_server():
    print("[Flask] App aktiv auf http://localhost:5000")
    flask_app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)


# --- 4. Socketify App (High-Performance Core, Port 8080) ---
def run_socketify_server():
    app = App()

    def get_node_handler(res, req):
        node_id = "reaktor_node_1"
        node = db.load_node(node_id)
        if not node:
            node = NodeGraphNode(node_id, {
                "system": "v1rtu4lyz1um_reaktor",
                "matrix": {"coordinates": [56.0, 1.618, 3.1415]}
            })
            db.save_node(node)
        
        res.write_header("Content-Type", "application/json")
        res.write_header("Access-Control-Allow-Origin", "*")
        res.end(json.dumps(node.data))

    app.get("/api/node", get_node_handler)
    print("[Socketify] High-Performance Gateway aktiv auf http://localhost:8080")
    app.listen(8080, lambda config: None)
    app.run()


# --- 5. Cheroot WSGI App (Port 8081) ---
def cheroot_wsgi_app(environ, start_response):
    path = environ.get('PATH_INFO', '')
    if path == '/api/health':
        data = {"status": "healthy", "engine": "cheroot + socketify + flask", "domain": "v1rtu4lyz1um.com"}
        body = json.dumps(data).encode('utf-8')
        start_response('200 OK', [('Content-Type', 'application/json'), ('Access-Control-Allow-Origin', '*')])
        return [body]
    start_response('404 Not Found', [('Content-Type', 'text/plain')])
    return [b'Not Found']

def run_cheroot_server():
    server = wsgi.Server(('127.0.0.1', 8081), cheroot_wsgi_app)
    print("[Cheroot] WSGI Server aktiv auf http://127.0.0.1:8081")
    server.start()


# --- 6. Multi-Server Orchestrierung ---
if __name__ == "__main__":
    # Flask auf Port 5000 im Hintergrund
    t_flask = threading.Thread(target=run_flask_server, daemon=True)
    t_flask.start()

    # Cheroot auf Port 8081 im Hintergrund
    t_cheroot = threading.Thread(target=run_cheroot_server, daemon=True)
    t_cheroot.start()

    # Socketify auf Port 8080 im Hauptthread
    run_socketify_server()
