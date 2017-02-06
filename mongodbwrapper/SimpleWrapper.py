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
        mquery, mproj, cmpquery = self.rewrite(sparql)
        mproj["_id"] = 0

        pipeline = []
        if len(mquery) > 0:
            pipeline.append({"$match": mquery})

        pipeline.append({"$project": mproj})
        if sparql.limit > 0:
            if sparql.offset > 0:
                pipeline.append({"$limit": int(sparql.limit) + int(sparql.offset)})
                pipeline.append({"$skip": int(sparql.offset)})
            else:
                pipeline.append({"$limit": int(sparql.limit)})
        res = []
        print "pipeline:", pipeline

        if len(cmpquery) > 0:
            result = self.collection.aggregate(pipeline)
            for r in result:
                for c in cmpquery:
                    if r[c] == cmpquery[c]:
                        del r[c]
                        res.append(r)
            return res

        return list(self.collection.aggregate(pipeline))

    def rewrite(self, sparql):

        triplepatterns, filters, optionals = self.decomposeQuery(sparql)

        qmap = []
        predobjmap = {}
        objpredmap = {}
        filtermap = {}
        predmap = {}

        for t in triplepatterns:
            if t.subject.constant:
                filtermap[self.mapping[0].subjecttemplate[1:-1]] = t.subject.name[1:-1]
            else:
                predobjmap[t.subject.name] = t.subject.name
                predmap[t.subject.name] = self.mapping[0].subjecttemplate[1:-1]

            if t.predicate.constant:

                if t.theobject.constant:
                    if "<" in t.theobject.name and '>' in t.theobject.name:
                        value = str(t.theobject.name[1:-1])
                    else:
                        value = str(t.theobject.name.replace('"', ''))

                    if t.predicate.name in filtermap:
                        if type(filtermap[t.predicate.name]) == dict:
                            filtermap[t.predicate.name]["$in"].append(value)
                        else:
                            filtermap[t.predicate.name] = {"$in": [filtermap[t.predicate.name]]}
                            filtermap[t.predicate.name]["$in"].append(value)
                    else:
                        filtermap[t.predicate.name] = value
                else:
                    predobjmap[t.predicate.name] = t.theobject.name
                    if t.theobject.name in objpredmap:
                        if type(objpredmap[t.theobject.name]) == list:
                            objpredmap[t.theobject.name].append(t.predicate.name)
                        else:
                            objpredmap[t.theobject.name] = [objpredmap[t.theobject.name]]
                            objpredmap[t.theobject.name].append(t.predicate.name)
                    else:
                        objpredmap[t.theobject.name] = t.predicate.name
                qmap.append(t.predicate.name)

        for p in self.mapping[0].predicates:
            if p.predicate in qmap:
                if (p.predicate, p.refmap.name) not in predmap:
                    predmap[p.predicate] = p.refmap.name
        mquery = {}
        cmpquery = {}
        mproj = {}
        if self.mapping[0].subjecttemplate[1:-1] in filtermap:
            mquery[self.mapping[0].subjecttemplate[1:-1]] = filtermap[self.mapping[0].subjecttemplate[1:-1]]
        args = [a.name for a in sparql.args]

        for k in predmap:
            v = predmap[k]
            if k in filtermap:
                mquery[v] = filtermap[k]
            if predobjmap[k] in args:
                mproj[predobjmap[k][1:]] = "$" + v
            if predobjmap[k] in objpredmap and type(objpredmap[predobjmap[k]]) == list:
                cm = {'$cmp': []}
                for o in objpredmap[predobjmap[k]]:
                    cm['$cmp'].append("$" + predmap[o])
                mproj['cmp_'+predobjmap[k][1:]] = cm

                cmpquery['cmp_'+predobjmap[k][1:]] = 0

        sparqlfilters = self.getFilters(filters, predmap, predobjmap)

        for f in sparqlfilters:
            if f in mquery:
                if type(mquery[f]) == dict:
                    if type(sparqlfilters[f]) == dict:
                        mquery[f].update(sparqlfilters[f])
                    else:
                        mquery[f]["$in"].append(sparqlfilters[f])
                else:
                    if type(sparqlfilters[f]) == dict:
                        mquery[f] = {"$eq": mquery[f]}
                        mquery[f].update(sparqlfilters[f])
                    else:
                        mquery[f] = {"$in": [mquery[f]]}
                        mquery[f]["$in"].append(sparqlfilters[f])
            else:
                mquery[f] = sparqlfilters[f]

        return mquery, mproj, cmpquery

    def getFilters(self, filters, predmap, predobjmap):
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
                    left = left.name
                    l = left

                right = f.expr.right
                if right.constant:
                    if "<" in right.name:
                        right = "'" + right.name[1:-1] + "'"
                    else:
                        right = right.name
                    r = right
                else:
                    right = right.name
                    l = right
                if "'" not in r and '"' not in r:
                    r = int(r)
                else:
                    r = r.replace('"', '').replace("'", '')
                op = "$eq"
                if f.expr.op == '>':
                    op = "$gt"
                elif f.expr.op == '<':
                    op = "$lt"
                elif f.expr.op == '>=':
                    op = "$gte"
                elif f.expr.op == '<=':
                    op = "$lte"
                elif f.expr.op == '!=':
                    op = "$ne"

                for k in predobjmap:
                    v = predobjmap[k]
                    if v == l:
                        for kk, vv in predmap:
                            if k == kk:
                                if op == "$eq":
                                    fquery[vv] = r
                                else:
                                    fquery[vv] = {op: r}

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