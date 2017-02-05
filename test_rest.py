
import urllib
import httplib

if __name__ == "__main__":
    query = '''
        prefix bsbm-inst: <http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/instances/>
        prefix bsbm: <http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/vocabulary/>
        prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        SELECT DISTINCT ?product WHERE {
                ?product bsbm:productFeature <http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/instances/ProductFeature34439>.
                ?product bsbm:productPropertyNumeric1 ?value1 .
                ?product bsbm:productFeature <http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/instances/ProductFeature892> .
                ?product <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/instances/ProductType1446>
        }
            limit 10
    '''
    params = urllib.urlencode({'query': query, 'molecule': 'http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/vocabulary/Product'})
    headers = {"Accept": "*/*", "Referer": 'http://localhost:27001/', "Host": 'localhost:27001'}
    # Establish connection and get response from server.
    conn = httplib.HTTPConnection('localhost:27001')
    # conn.set_debuglevel(1)
    conn.request("GET", "/sparql" + "?" + params, None, headers)

    response = conn.getresponse()

    # print response.status
    if (response.status == httplib.OK):
        res = response.read()
        print res
        if type(res) == dict:
            if 'result' in res:
                for x in res['results']:
                    print x