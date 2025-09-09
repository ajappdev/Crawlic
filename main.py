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

@app.route('/')
def home():
    return jsonify({
        "message": "SeleniumBase Flask API is running!",
        "endpoints": {
            "/": "This help message",
            "/test": "Test the driver with jsonplaceholder",
            "/navigate": "Navigate to a URL (POST with 'url' parameter)",
            "/status": "Check if driver is initialized"
        }
    })

@app.route('/test')
def test_driver():
    try:
        driver = get_driver()
        print("Navigating to test URL...")
        driver.get("https://jsonplaceholder.typicode.com/todos/1")
        time.sleep(2)  # Reduced sleep time for API responsiveness
        
        # Get page title and current URL
        page_title = driver.title
        current_url = driver.current_url
        
        # Try to get the JSON content if it's a JSON API
        try:
            page_source = driver.page_source
            # Extract JSON from the page if possible
            if "application/json" in driver.execute_script("return document.contentType") or True:
                json_start = page_source.find('{')
                json_end = page_source.rfind('}') + 1
                if json_start != -1 and json_end > json_start:
                    json_content = page_source[json_start:json_end]
                    parsed_json = json.loads(json_content)
                else:
                    parsed_json = None
            else:
                parsed_json = None
        except Exception as e:
            parsed_json = None
        
        return jsonify({
            "status": "success",
            "page_title": page_title,
            "current_url": current_url,
            "json_content": parsed_json,
            "message": "Driver test completed successfully"
        })
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/navigate', methods=['POST'])
def navigate():
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({
                "status": "error",
                "message": "Please provide 'url' in JSON body"
            }), 400
        
        url = data['url']
        driver = get_driver()
        
        print(f"Navigating to: {url}")
        driver.get(url)
        time.sleep(1)
        
        page_title = driver.title
        current_url = driver.current_url
        
        return jsonify({
            "status": "success",
            "page_title": page_title,
            "current_url": current_url,
            "message": f"Successfully navigated to {url}"
        })
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/status')
def status():
    global driver_instance
    return jsonify({
        "driver_initialized": driver_instance is not None,
        "status": "Flask app is running"
    })

@app.route('/quit', methods=['POST'])
def quit_driver():
    global driver_instance
    try:
        if driver_instance:
            driver_instance.quit()
            driver_instance = None
            return jsonify({
                "status": "success",
                "message": "Driver quit successfully"
            })
        else:
            return jsonify({
                "status": "info",
                "message": "No driver instance to quit"
            })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == "__main__":
    print("Starting Flask app with SeleniumBase...")
    app.run(host='0.0.0.0', port=5000, debug=True)