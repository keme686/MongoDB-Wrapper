#!/usr/bin/env python

from flask import Flask, request
from flask.json import jsonify
import sys
import os
import getopt

from mongodbwrapper.SimpleWrapper import SimpleWrapper

app = Flask(__name__)


@app.route("/sparql", methods=['POST', 'GET'])
def sparql():
    if request.method == 'GET':
        try:
            molecule = request.args.get("molecule", '')
            query = request.args.get("query", '')
            query = query.replace('\n', ' ').replace('\r', ' ')
            print 'query:', query
            sw = SimpleWrapper(molecule, mapping)
            res = sw.exeQuery(query)

            return jsonify({"result": res})
        except Exception as e:
            print "Exception", e
            print {"result": [], "error": e.message}
            return jsonify({"result": [], "error": e.message})
    else:
        return jsonify({"result": [], "error": "Invalid HTTP method used. Use GET "})


def usage():
    usage_str = ("Usage: {program} -p <port>  -m <path_to_mapping_file>  "
                 + "\n where \n<port> "
                 + " is port for this wrapper \n<path_to_mapping_file> "
                   " is path to mapping file (.ttl, .nt, ..) for this wrapper"
                 + "\n")

    print usage_str.format(program=sys.argv[0]),


if __name__ == "__main__":

    mapping = ""
    argv = sys.argv

    port = 5000
    i = 0
    for a in argv:
        i += 1
        if i + 1 > len(argv):
            break
        if argv[i] == "-p":
            port = argv[i+1]
        if argv[i] == "-m":
            mapping = os.path.abspath(argv[i+1])

    if not mapping or len(mapping) == 0:
        print "maping is empty"
        print port
        usage()
        sys.exit(1)
    print port, mapping
    app.run(port=port, host="0.0.0.0")
