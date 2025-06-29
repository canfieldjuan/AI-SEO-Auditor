from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
import os

def create_app():
    app = Flask(__name__)
    CORS(app)

    # Create necessary directories
    os.makedirs('reports', exist_ok=True)
    os.makedirs('cache', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    os.makedirs('static', exist_ok=True)

    # Basic routes
    @app.route('/')
    def index():
        if os.path.exists('static/index.html'):
            return send_from_directory('static', 'index.html')
        else:
            return "Index.html not found in static directory"

    @app.route('/health')
    def health_check():
        return jsonify({'status': 'healthy', 'version': '2.0.0'})
    
    @app.route('/api/test')
    def test_api():
        return jsonify({'message': 'API is working!'})

    # Try to import and register the API blueprint
    try:
        from routes.api_routes import api_bp
        app.register_blueprint(api_bp, url_prefix='/api')
        print("✓ API routes registered successfully")
    except Exception as e:
        print(f"✗ Failed to register API routes: {e}")
        
        # Add a fallback audit endpoint for testing
        @app.route('/api/audit', methods=['POST'])
        def fallback_audit():
            return jsonify({
                'success': False,
                'error': f'API routes not properly loaded: {str(e)}'
            })
    
    # Try to initialize database
    try:
        from models.database import init_database
        init_database()
        print("✓ Database initialized successfully")
    except Exception as e:
        print(f"✗ Failed to initialize database: {e}")
    
    # Try to setup logging
    try:
        from utils.logging_config import setup_logging
        setup_logging(app)
        print("✓ Logging configured successfully")
    except Exception as e:
        print(f"✗ Failed to setup logging: {e}")
    
    print(f"\nRegistered routes:")
    for rule in app.url_map.iter_rules():
        print(f"  {rule.endpoint}: {rule.rule}")
    
    return app

if __name__ == '__main__':
    print("Starting Flask application...")
    app = create_app()
    print("\nFlask is running on http://127.0.0.1:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)