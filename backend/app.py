from flask import Flask, request, jsonify
from flask_cors import CORS
from convert import detect_framework, parse_qiskit, parse_cirq

app = Flask(__name__)
CORS(app)

@app.route("/to_qasm", methods=["POST"])
def to_qasm():
    code = request.json.get("code", "")
    framework = detect_framework(code)

    try:
        if framework == "qiskit":
            qasm = parse_qiskit(code)
        elif framework == "cirq":
            qasm = parse_cirq(code)
        else:
            return jsonify({"success": False, "error": "Unknown framework"})
        return jsonify({"success": True, "qasm": qasm})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == "__main__":
    app.run(debug=True)
