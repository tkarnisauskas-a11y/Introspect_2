from flask import Flask, jsonify
import os
import json
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.config.settings import Config
from src.services.claims_service import ClaimsService

app = Flask(__name__)
config = Config()
claims_service = ClaimsService(config)

@app.route('/claims/<claim_id>', methods=['GET'])
def get_claim(claim_id):
    try:
        claim = claims_service.get_claim(claim_id)
        if claim:
            return jsonify(claim)
        return jsonify({'error': 'Claim not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)