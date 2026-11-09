from flask import Flask, render_template, jsonify, request
import os
from models import Player, PlasticResource, MathDiscovery, engine, init_db
from sqlalchemy.orm import sessionmaker
from game_logic import RiemannianGameLogic, PlasticToPhysicalConverter

app = Flask(__name__)
Session = sessionmaker(bind=engine)
game_logic = RiemannianGameLogic()
converter = PlasticToPhysicalConverter()

# Initialize DB on start
init_db()

@app.route('/')
def index():
    return render_template('templates/index.html')

@app.route('/api/status')
def status():
    return jsonify({
        "status": "online",
        "game_mode": "AR-XAI-OpenWorld",
        "discovery": "Riemannian Manifold Exploration"
    })

@app.route('/api/explore', methods=['POST'])
def explore():
    discovery = game_logic.explore_manifold()
    session = Session()
    new_discovery = MathDiscovery(
        manifold_type=discovery['type'],
        curvature_metric=discovery['curvature'],
        coordinates=str(discovery['coords'])
    )
    session.add(new_discovery)
    session.commit()
    session.close()
    return jsonify(discovery)

@app.route('/api/collect', methods=['POST'])
def collect():
    data = request.json
    plastic_type = data.get('type', 'PET')
    weight = data.get('weight', 0)

    result = converter.process_plastic(plastic_type, weight)

    session = Session()
    resource = PlasticResource(type=plastic_type, weight_grams=weight)
    session.add(resource)
    session.commit()
    session.close()

    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
