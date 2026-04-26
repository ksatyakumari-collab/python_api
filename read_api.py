from flask import Flask, jsonify, request, abort

app = Flask(__name__)

def _extract_body_as_string(req):
    # Try JSON first (if the client sent a raw JSON string it will come here).
    if req.is_json:
        payload = req.get_json(silent=True)
        # If payload is a JSON string, return it; otherwise return the whole payload
        return payload if isinstance(payload, str) else payload
    # Fallback to raw body text
    data = req.get_data(as_text=True)
    return data if data else None

# GET /api/values
@app.route('/api/values', methods=['GET'])
def get_values():
    # Mimic the original C# return: new string[] { "value1", "value2" }
    return jsonify(["value1", "value2"])

# GET /api/values/<id>
@app.route('/api/values/<int:id>', methods=['GET'])
def get_value(id):
    # Mimic the original C# return: "value"
    return jsonify("value")

# POST /api/values
@app.route('/api/values', methods=['POST'])
def post_value():
    value = _extract_body_as_string(request)
    # No storage implemented — mirror original empty method.
    # Return 201 Created to indicate resource accepted (adjust as needed).
    return ('', 201)

# PUT /api/values/<id>
@app.route('/api/values/<int:id>', methods=['PUT'])
def put_value(id):
    value = _extract_body_as_string(request)
    # No storage implemented — mirror original empty method.
    # Return 204 No Content to indicate success with no body.
    return ('', 204)

# DELETE /api/values/<id>
@app.route('/api/values/<int:id>', methods=['DELETE'])
def delete_value(id):
    # No deletion logic implemented — mirror original empty method.
    return ('', 204)

if __name__ == '__main__':
    # For development only. In production use a WSGI server (gunicorn/uwsgi).
    app.run(host='127.0.0.1', port=5000, debug=True)