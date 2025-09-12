from flask import Flask, jsonify, request
import common as common
import time
import json

app = Flask(__name__)

# Store driver instance (you might want to manage this differently in production)
driver_instance = None

def get_driver():
    global driver_instance
    if driver_instance is None:
        print("Initializing new driver...")
        driver_instance = common.initiate_driver(False, False, True)
    return driver_instance

@app.route('/get-page-content', methods=['POST'])
def get_page_content():
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

@app.route('/find-contact-email', methods=['POST'])
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
    app.run(host='0.0.0.0', port=5000, debug=True)