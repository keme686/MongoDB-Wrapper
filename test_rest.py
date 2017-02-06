
import urllib
import httplib

if __name__ == "__main__":
    query = '''
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX rev: <http://purl.org/stuff/rev#>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        PREFIX bsbm: <http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/vocabulary/>
        PREFIX dc: <http://purl.org/dc/elements/1.1/>
        SELECT ?reviewer ?revPublisher
        WHERE {
            ?reviewer a <http://xmlns.com/foaf/0.1/Person>.
            ?reviewer dc:date "2008-09-05" .
            ?reviewer dc:publisher ?revPublisher
        } limit 10
    '''
    query = '''
        PREFIX bsbm-inst: <http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/instances/>
        PREFIX bsbm: <http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/vocabulary/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        SELECT DISTINCT ?product ?label
        WHERE {
        ?product rdfs:label ?label .
        ?product a <http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/instances/ProductType1446> .
        ?product bsbm:productFeature <http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/instances/ProductFeature34439> .
        ?product bsbm:productFeature <http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/instances/ProductFeature892> .
        ?product bsbm:productPropertyNumeric1 ?value1 .
        FILTER (?value1 > 136)
        }
        ORDER BY ?label
    '''
    params = urllib.urlencode({'query': query, 'molecule': 'http://xmlns.com/foaf/0.1/Person'})
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