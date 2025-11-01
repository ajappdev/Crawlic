# General imports
from datetime import datetime
import secrets
from functools import wraps
from urllib.parse import quote_plus
import json
import os
import time

# flask imports
from flask_swagger_ui import get_swaggerui_blueprint
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

# Celery imports
import celery_app as celery_app

# App imports
import common as common
import ai as ai

# Flask app config
app = Flask(__name__)
CORS(app)

########################################
# Swagger UI Configuration
########################################
SWAGGER_URL = '/api/docs'
API_URL = '/static/swagger.json'

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Web Scraping API"
    }
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

########################################
# Initialize the database
########################################

encoded_password = quote_plus(common.POSTGRES_PASSWORD)
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{common.POSTGRES_USER}:{encoded_password}@{common.POSTGRES_HOST}:{common.POSTGRES_PORT}/{common.POSTGRES_DB}"      
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(100))
    api_key = db.Column(db.String(64), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    usage_count = db.Column(db.Integer, default=0)

# create the database tables
with app.app_context():
    db.create_all()

########################################
# End Database Initialization
########################################

########################################
# Authentification Endpoints and wrappers
########################################

def require_api_key(func):
    """
    Decorator to require API key authentication for endpoints.
    Checks for 'Authorization' header with Bearer token.
    RETURNS:
        401 if missing, 403 if invalid, otherwise proceeds to the endpoint.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        auth = request.headers.get("Authorization")
        if not auth or not auth.startswith("Bearer "):
            return jsonify({"msg": "Missing API key"}), 401

        key = auth.split(" ")[1]
        client = Client.query.filter_by(api_key=key).first()
        if not client:
            return jsonify({"msg": "Invalid API key"}), 403

        client.usage_count += 1
        db.session.commit()

        return func(*args, **kwargs)
    return wrapper

@app.route("/api/register", methods=["POST"])
def register():
    """
    Registers a new client and generates an API key.
    Expects JSON body with 'name' and 'email'.
    RETURNS:
        JSON response with the generated API key.
    """
    data = request.get_json()
    if "name" not in data or "email" not in data:
        return jsonify({"error": "Name and email are required"}), 400

    key = secrets.token_hex(32)

    client = Client(
        name=data.get("name"),
        email=data.get("email"),
        api_key=key)
    
    db.session.add(client)
    db.session.commit()

    return jsonify(
        {
            "message": "Client registered successfully",
            "api_key": key
        }, 201
    )

########################################
# End Authentification Endpoints and wrappers
########################################

########################################
# Task Status Endpoint
########################################

@app.route('/api/task/<task_id>', methods=['GET'])
@require_api_key
def get_task_status(task_id):
    """
    Check the status of an async task.
    Returns task state and result if completed.
    """
    task = celery_app.celery.AsyncResult(task_id)
    
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'status': 'Task is waiting in queue...',
            'progress': 0
        }
    elif task.state == 'STARTED':
        response = {
            'state': task.state,
            'status': 'Task is processing...',
            'progress': 30
        }
    elif task.state == 'PROGRESS':
        response = {
            'state': task.state,
            'status': task.info.get('status', 'Processing...'),
            'progress': 60
        }
    elif task.state == 'SUCCESS':
        result = task.result
        response = {
            'state': task.state,
            'status': 'Task completed successfully',
            'progress': 100,
            'result': result
        }
    elif task.state == 'FAILURE':
        response = {
            'state': task.state,
            'success': False,
            'status': 'Task failed',
            'error': str(task.info),
            'progress': 0
        }
    else:
        response = {
            'state': task.state,
            'status': str(task.info),
            'progress': 0
        }
    
    return jsonify(response)

########################################
# Scraping Endpoints (Async with Celery)
########################################


@app.route('/api/page-content', methods=['POST'])
@require_api_key
def get_page_content():
    """
    Queue a task to get page content asynchronously.
    Returns immediately with task_id for status checking.
    """
    try:
        data = request.get_json()
        if not data or "link" not in data:
            return jsonify({
                "success": False,
                "error": "Missing 'link' in request payload"
            }), 400

        link = data["link"]

        # Queue the task
        task = celery_app.scrape_page_content_task.apply_async(args=[link])

        return jsonify({
            "success": True,
            "task_id": task.id,
            "status_url": f"/api/task/{task.id}",
            "message": "Task queued successfully. Use task_id to check status."
        }), 202
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/describe-page', methods=['POST'])
@require_api_key
def describe_page():
    try:
        # Validate JSON body
        data = request.get_json()
        if not data or "link" not in data:
            return jsonify({
                "success": False,
                "error": "Missing 'link' in request payload"
            }), 400

        link = data["link"]

        task = celery_app.scrape_page_content_task.apply_async(args=[link])

        return jsonify({
            "success": True,
            "task_id": task.id,
            "status_url": f"/api/task/{task.id}",
            "message": "Task queued successfully. Use task_id to check status."
        }), 202
    
    except Exception as e:
        # In production, log the error instead of exposing str(e)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/custom-page-content', methods=['POST'])
@require_api_key
def custom_page_content():
    try:
        data = request.get_json()
        if not data or 'link' not in data:
            return jsonify({"success": False, "error": "Missing 'link' in request payload"}), 400
        elif 'user_query' not in data:
            return jsonify({"success": False, "error": "Missing 'user_query' in request payload"}), 400
        elif 'output_format' not in data:
            return jsonify({"success": False, "error": "'output_format' cannot be empty"}), 400
    
        link = data['link']
        user_query = data['user_query']
        output_format = data['output_format']

        task = celery_app.custom_page_content_task.apply_async(args=[link, output_format, user_query])

        return jsonify({
            "success": True,
            "task_id": task.id,
            "status_url": f"/api/task/{task.id}",
            "message": "Task queued successfully. Use task_id to check status."
        }), 202
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/get-answer-from-page', methods=['POST'])
@require_api_key
def get_answer_from_page():
    try:
        data = request.get_json()
        if not data or 'link' not in data:
            return jsonify({"success": False, "error": "Missing 'link' in request payload"}), 400
        elif 'user_query' not in data:
            return jsonify({"success": False, "error": "Missing 'user_query' in request payload"}), 400
    
        link = data['link']
        user_query = data['user_query']

        task = celery_app.get_answer_from_page_task.apply_async(args=[link, user_query])

        return jsonify({
            "success": True,
            "task_id": task.id,
            "status_url": f"/api/task/{task.id}",
            "message": "Task queued successfully. Use task_id to check status."
        }), 202
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
        

@app.route('/api/find-contact-email', methods=['POST'])
@require_api_key
def find_contact_email():
    try:
        data = request.get_json()
        if not data or 'link' not in data:
            return jsonify({"success": False, "error": "Missing 'link' in request payload"}), 400
    
        link = data['link']

        task = celery_app.find_contact_email_task.apply_async(args=[link])

        return jsonify({
            "success": True,
            "task_id": task.id,
            "status_url": f"/api/task/{task.id}",
            "message": "Task queued successfully. Use task_id to check status."
        }), 202
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

########################################
# Health Check
########################################

@app.route('/api/health', methods=['GET'])
def health():
    """Check if the API is running"""
    return jsonify({
        'status': 'healthy',
        'redis': os.getenv('REDIS_URL', 'not configured')
    }), 200

    
if __name__ == "__main__":
    print("Starting Flask app with Celery + Redis...")
    app.run(host='0.0.0.0', port=9500, debug=True)