from nose.tools import *
from bin.concept_lattice_manager import *
from bin.db_stuff import DBHelper
from data.fake.fake_dataset import *

@nottest
def test_node():
    Node.destringizer('attr_set:0 1 2 6 ;obj_set:5 ;supp:1')

@nottest
def test_parse_lattice():
    lattice = ConceptLattice.parse_lattice('books_5k.gml')
    def count_nodes_and_edges(lattice):
        print len(lattice.graph.nodes()), len(lattice.graph.edges())
    count_nodes_and_edges(lattice)

@nottest
def test_build_bg():
    bg = Background.build_bg_from_db()

@nottest
def test_gen_lattice_use_db():
    bg = Background.build_bg_from_db('trans_books_1k', 'facet_codes_1k')
    fcl_miner = FCLMiner(bg)
    lattice = fcl_miner.gen_lattice()
    lattice.save_lattice('books_1k.gml')
    print len(lattice.graph.nodes()), len(lattice.graph.edges())

@nottest
def test_get_depth():
    lattice = ConceptLattice.parse_lattice('books_1k.gml')
    print lattice.depth

@nottest
def test_get_root_and_leaf():
    lattice = ConceptLattice.parse_lattice('draft.gml')
    
    print len(lattice.leaf_nodes)
    print lattice.get_average_supp(lattice.leaf_nodes)
    print lattice.get_average_supp(lattice.graph.nodes())
    print lattice.depth

@nottest
def test_fast_add_intent():
    sql1 = u"""
           select id, draftYear_id, draftFrom_id, tmId_id, draftOverall_id from trans_basketball_draft; 
         """ 
    session = DBHelper.get_session()
    draft = session.execute(sql1).fetchall()
    objs_r = [(id ,set([draftYear_id, draftFrom_id, tmId_id, draftOverall_id])) \
            for id,draftYear_id, draftFrom_id, tmId_id, draftOverall_id in draft]
    fast_add_intent_algo = ConceptLatticeFactory(objs_r)
    lattice = fast_add_intent_algo.create_lattice_incrementally()
    lattice.save_lattice('draft.gml')
    print fast_add_intent_algo.total_steps, fast_add_intent_algo.skip_steps 

@nottest
def test_expand_and_refine():
    lattice = ConceptLattice.parse_lattice('test.gml')
    query_attr_set = set([0,4,5,6,7,8])
    node = lattice.locate(query_attr_set)
    result = lattice.expand(node, 1) 
    for n in result:
        print n.obj_set,
        
@nottest
def test_fake_dataset():
    name = 'fake_10000_50_0.10'
    dataset = get_dataset('data/fake/%s.csv' % name)
    objs_r = [(i, obj) for i,obj in enumerate(dataset)]
    fast_add_intent_algo = ConceptLatticeFactory(objs_r)
    lattice = fast_add_intent_algo.create_lattice_incrementally()
    lattice.save_lattice('%s.gml' % name)
    print fast_add_intent_algo.total_steps, fast_add_intent_algo.skip_steps 

@istest
def test_fast_add_intent_books():
    sql1 = u"""
           select book_id, author_id, publisher_id, year_id from trans_books_20k; 
         """ 
    session = DBHelper.get_session()
    books = session.execute(sql1).fetchall()
    objs_r = [(book_id ,set([author_id, publisher_id, year_id])) \
            for book_id, author_id, publisher_id, year_id in books]
    fast_add_intent_algo = ConceptLatticeFactory(objs_r)
    lattice = fast_add_intent_algo.create_lattice_incrementally()
    lattice.save_lattice('/root/FCA_Facet/data/books_20k.gml')
    print fast_add_intent_algo.total_steps, fast_add_intent_algo.skip_steps 

   
