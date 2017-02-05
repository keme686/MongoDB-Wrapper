from mongodbwrapper.SimpleWrapper import SimpleWrapper

if __name__ == "__main__":
    sw = SimpleWrapper("http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/vocabulary/Product", "xmlmapping.ttl")
    query = '''
        prefix bsbm-inst: <http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/instances/>
        prefix bsbm: <http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/vocabulary/>
        prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        SELECT ?product WHERE {
                ?product bsbm:productFeature <http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/instances/ProductFeature8000> .
                ?product <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/instances/ProductType1267> .
                ?product bsbm:productFeature ?pf .
                ?product bsbm:productPropertyNumeric1 ?p1 .
                ?product bsbm:productPropertyNumeric3 ?p3
        FILTER ((?p1 > 228)) .
        FILTER ((?p3 < 156)) .
        FILTER ((?pf != <http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/instances/ProductFeature8001>))

        } LIMIT 10000 OFFSET 0
    '''
    #sw.rewrite(query)
    cur = sw.exeQuery(query)

    for d in cur:
        print d