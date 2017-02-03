from flask import Flask, request
from flask.json import jsonify
import json
from mongodbwrapper.SimpleWrapper import SimpleWrapper

app = Flask(__name__)

@app.route("/sparql", methods=['POST', 'GET'])
def sparql():
    if request.method == 'GET':
        try:
            molecule = request.args.get("molecule", '')
            query = request.args.get("query", '')
            query = query.replace('\n', ' ').replace('\r', ' ')
            sw = SimpleWrapper(molecule, mapping)
            res = sw.exeQuery(query)
            return jsonify({"result": res})
        except Exception as e:
            print e
            return jsonify({"result": [], "error": e.message})
    else:
        return jsonify({"result": [], "error": "Invalid HTTP method used. Use GET "})

if __name__ == "__main__":
    with open("../config") as f:
        conf = json.load(f)
    mapping = conf["mapping"]
    app.run()