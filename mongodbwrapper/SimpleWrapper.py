from mongodbwrapper.parser import queryParser as qp
from mongodbwrapper.mapping.RMLMapping import *
from mongodbwrapper.parser.services import *
from pymongo import MongoClient


class SimpleWrapper(object):
    def __init__(self, molecule, mapping, mongourl=None):
        self.molecule = molecule
        self.mappingfile = mapping
        self.mapping = RMLMapping(self.mappingfile).getMapping(self.molecule)
        if mongourl is not None:
            self.client = MongoClient(mongourl)
        elif self.mapping[0].server is not None and len(self.mapping[0].server) > 0:
            self.client = MongoClient(self.mapping[0].server)
        else:
            self.client = MongoClient("localhost:27017")

        self.db = self.client.get_database(self.mapping[0].databaseName)
        self.collection = self.db.get_collection(self.mapping[0].collectionName)

    def exeQuery(self, query):
        sparql = qp.parse(query)
        mquery, mproj, predmap = self.rewrite(sparql)
        mproj["_id"] = 0
        agg = []

        if len(mquery) > 0:
            agg.append({"$match": mquery})
        agg.append({"$project": mproj})
        if sparql.limit > 0:
            if sparql.offset > 0:
                agg.append({"$limit":int(sparql.limit) + int(sparql.offset)})
                agg.append({"$skip": int(sparql.offset)})
            else:
                agg.append({"$limit": int(sparql.limit)})
        return list(self.collection.aggregate(agg))

    def rewrite(self, sparql):

        triplepatterns, filters, optionals = self.decomposeQuery(sparql)

        qmap = []
        predobjmap = {}
        filtermap = {}
        predmap = []

        for t in triplepatterns:
            if t.subject.constant:
                filtermap[self.mapping[0].subjecttemplate[1:-1]] = t.subject.name
            else:
                predobjmap[t.subject.name] = t.subject.name
                predmap.append((t.subject.name, self.mapping[0].subjecttemplate[1:-1]))

            if t.predicate.constant:
                predobjmap[t.predicate.name] = t.theobject.name
                qmap.append(t.predicate.name)
                if t.theobject.constant:
                    if "<" in t.theobject.name and '>' in t.theobject.name:
                        filtermap[t.predicate.name] = str(t.theobject.name[1:-1])
                    else:
                        filtermap[t.predicate.name] = str(t.theobject.name.replace('"', ''))

        for p in self.mapping[0].predicates:
            if p.predicate in qmap:
                predmap.append((p.predicate, p.refmap.name))
        mquery = {}
        mproj = {}
        args = [a.name for a in sparql.args]
        for k, v in predmap:
            if k in filtermap:
                mquery[v] = filtermap[k]
            if predobjmap[k] in args:
                mproj[predobjmap[k][1:]] = "$"+v

        #sparqlfilters = self.getFilters(filters)

        return mquery, mproj, predmap

    def getFilters(self, filters):
        qfs = []
        fquery = {}
        for f in filters:
            r = ""
            l = ""
            if isinstance(f.expr.left, Argument) and isinstance(f.expr.right, Argument):
                left = f.expr.left
                if left.constant:
                    if "<" in left.name:
                        left = "'" + left.name[1:-1] + "'"
                    else:
                        left = left.name
                    r = left
                else:
                    left = left.name[1:]
                    l = left

                right = f.expr.right
                if right.constant:
                    if "<" in right.name:
                        right = "'" + right.name[1:-1] + "'"
                    else:
                        right = right.name
                    r = right
                else:
                    right = right.name[1:]
                    l = right
                if "'" not in r and '"' not in r:
                    r = "'" + r + "'"
                qfs.append(l + " " + f.expr.op + " " + r)
        qfs = " and ".join(map(str, qfs))

        return fquery
    def decomposeQuery(self, query):
        """
        decomposes a query to set of Triples and set of Filters
        :param query: sparql
        :return: triple composed of triplepatters, filters and optional
        """
        tp = []
        filters = []
        opts = []
        for b in query.body.triples:  # UnionBlock
            if isinstance(b, JoinBlock):
                for j in b.triples:  # JoinBlock
                    if isinstance(j, Triple):
                        if j.subject.constant:
                            j.subject.name = getUri(j.subject, getPrefs(query.prefs))
                        if j.predicate.constant:
                            j.predicate.name = getUri(j.predicate, getPrefs(query.prefs))
                        if j.theobject.constant:
                            j.theobject.name = getUri(j.theobject, getPrefs(query.prefs))
                        tp.append(j)
                    if isinstance(j, Filter):
                        filters.append(j)
                    elif isinstance(j, Optional):
                        opts.append(j)
        return tp, filters, opts


if __name__ == "__main__":
    sw = SimpleWrapper("http://xmlns.com/foaf/0.1/Person", "../csvmapping.ttl")
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
    #sw.rewrite(query)
    cur = sw.exeQuery(query)
    print cur
    for d in cur:
        print d