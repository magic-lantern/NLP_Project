#
#  from https://www.youtube.com/watch?v=5DCS9LE-8rE
#
import rdflib
from rdflib.graph import ConjunctiveGraph, Graph
from rdflib.plugins.sparql import prepareQuery

g = ConjunctiveGraph()

# default rdflib parsers
#   https://rdflib.readthedocs.org/en/stable/plugin_parsers.html
# rdflib doesn't support JSON format without an extension
#   can use https://github.com/RDFLib/rdflib-jsonld to add that capability

g.parse("http://dbpedia.org/data/Python_(programming_language).ntriples", format="nt")

# for o,p,s in g:
#     print("o: ", o)
#     print("p: ", p)
#     print("s: ", s)
#
# for triple in g:
#     print(triple)

r = list(g.triples((None, rdflib.URIRef('rdf:about'), None)))

print(r)

out = g.serialize(format="pretty-xml")
print(out)

# need to write out in binary format - because of unicode?
#outfile = open("test.xml", 'wb')
#outfile.write(g.serialize(format="pretty-xml"))

q = prepareQuery('''
SELECT ?object WHERE
{ ?language dbpedia:influenced ?object. }''',
                initNs = {'dbpedia': 'http://dbpedia.org/ontology/'})
g = Graph()
g.parse('http://live.dbpedia.org/data/Programming_languages.ntriples', format='nt')

python = rdflib.URIRef('http://dbpedia.org/resource/Python_(programming_language)')
for row in g.query(q, initBindings={'language':python}):
    print(row.uri)
