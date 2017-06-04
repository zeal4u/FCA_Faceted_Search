from nose.tools import *
from bin.search_engine import *
from bin.concept_lattice_manager import *


@istest
def test_key_word_search():
    lattice = ConceptLattice.parse_lattice('/root/FCA_Facet/data/books_5k.gml')
    search_service = SearchService(lattice=lattice)
    result = search_service.key_word_search(['snow'])
    print 'node type',lattice.graph.node[search_service.cur_node]['type']
    #print result.content
    #print result.facets
    result = search_service.refine_search(0.95)
