from mongodbwrapper.SimpleWrapper import SimpleWrapper

if __name__ == "__main__":
    sw = SimpleWrapper("http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/vocabulary/Product", "xmlmapping.ttl")
    query = '''
        prefix bsbm-inst: <http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/instances/>
        prefix bsbm: <http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/vocabulary/>
        prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        SELECT DISTINCT ?product WHERE {
                ?product bsbm:productFeature <http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/instances/ProductFeature34439> .
                ?product bsbm:productPropertyNumeric1 ?value1 .
                ?product bsbm:productFeature <http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/instances/ProductFeature892> .
                ?product <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/instances/ProductType1446>
        FILTER ((?value1 > 136))

        }
            limit 10
    '''
    #sw.rewrite(query)
    cur = sw.exeQuery(query)

    for d in cur:
        print d