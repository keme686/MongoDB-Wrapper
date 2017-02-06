from mongodbwrapper.SimpleWrapper import SimpleWrapper

if __name__ == "__main__":
    sw = SimpleWrapper("http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/vocabulary/Product", "xmlmapping.ttl")
    query = '''
        PREFIX bsbm-inst: <http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/instances/>
        PREFIX bsbm: <http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/vocabulary/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        prefix dc: <http://purl.org/dc/elements/1.1/>
        SELECT DISTINCT ?p ?f ?propertyNumeric2  ?propertyNumeric1 ?propertyTextual2
        WHERE {
            <http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/instances/dataFromProducer1/Product1> bsbm:productPropertyNumeric2 ?propertyNumeric2 .
            <http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/instances/dataFromProducer1/Product1> bsbm:productPropertyTextual2 ?propertyTextual2 .
            <http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/instances/dataFromProducer1/Product1> bsbm:producer ?p .
            <http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/instances/dataFromProducer1/Product1> bsbm:productPropertyNumeric1 ?propertyNumeric1 .
            <http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/instances/dataFromProducer1/Product1> dc:publisher ?p .
           <http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/instances/dataFromProducer1/Product1> bsbm:productFeature ?f
        } limit 10
    '''
    #sw.rewrite(query)
    cur = sw.exeQuery(query)
    print len(cur)
    for d in cur:
        print d

