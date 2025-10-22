# General imports
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import secrets
from functools import wraps
from flask_swagger_ui import get_swaggerui_blueprint
from urllib.parse import quote_plus

# App imports
import common as common
import ai as ai

# Flask app config
app = Flask(__name__)

########################################
# Swagger UI Configuration
########################################
SWAGGER_URL = '/api/docs'  # URL for exposing Swagger UI (without trailing '/')
API_URL = '/static/swagger.json'  # Our API url (can be a local file or URL)

# Call factory function to create our blueprint
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
print(encoded_password)
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

@app.route("/register", methods=["POST"])
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
# Scraping Endpoints
########################################

@app.route('/page-content', methods=['GET'])
@require_api_key
def get_page_content():
    """
    This endpoint returns the content of the web page (link) provided in
    the body
    """
    try:
        # Validate JSON body
        data = request.get_json()
        if not data or "link" not in data:
            return jsonify({
                "success": False,
                "error": "Missing 'link' in request payload"
            }), 400

        link = data["link"]

        # Call your logic
        content = common.get_source_content(link)

        # Return structured response
        return jsonify({
            "success": True,
            "data": {
                "link": link,
                "content": content
            }
        }), 200
    
    except Exception as e:
        # In production, log the error instead of exposing str(e)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/describe-page', methods=['GET'])
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

        # Call the existing endpoint internally
        content = common.get_source_content(link)
        
        # Analyze content using AI module
        description = ai.describe_web_page_content(content)
        
        # Return structured response
        return jsonify({
            "success": True,
            "data": {
                "content": content,
                "summary": description.summary,
                "type": description.type
            }
        }), 200
    
    except Exception as e:
        # In production, log the error instead of exposing str(e)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/find-contact-email', methods=['GET'])
@require_api_key
def find_contact_email():
    try:
        data = request.get_json()
        if not data or 'link' not in data:
            return jsonify({"success": False, "error": "Missing 'link' in request payload"}), 400
    
        emails = common.find_contact_email(data['link'])
        return jsonify({
            "success": True,
            "data": {
                "link": data['link'],
                "emails": emails
            }
        }), 200
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    
if __name__ == "__main__":
    print("Starting Flask app with SeleniumBase...")
    app.run(host='0.0.0.0', port=9500, debug=True)