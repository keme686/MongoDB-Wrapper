
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
    params = urllib.urlencode({'query': query, 'molecule': 'http://xmlns.com/foaf/0.1/Person'})
    headers = {"Accept": "*/*", "Referer": 'http://localhost:5000/', "Host": 'localhost:5000'}
    # Establish connection and get response from server.
    conn = httplib.HTTPConnection('localhost:5000')
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