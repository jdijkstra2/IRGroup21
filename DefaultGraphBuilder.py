import numpy as np
from scipy.spatial import distance
import json

from bglinking.database_utils import db_utils as db_utils
from bglinking.general_utils import utils
from bglinking.general_utils import group21_utils

from bglinking.graph.Node import Node
from bglinking.graph.graph_builders.InformalGraphBuilderInterface import InformalGraphBuilderInterface


class DefaultGraphBuilder(InformalGraphBuilderInterface):
    def build(self, graph, cursor, embeddings, index_utils, docid, use_entities, nr_terms=0, term_tfidf=0.0, term_position=0.0, text_distance=0.0, term_embedding=0.0):
        # Retrieve named entities from database.
        
        #print("Term_tfidf: ")
        #print(term_tfidf)

        #print("term_position:")
        #print(term_position)        

        if use_entities:
            entities = db_utils.get_entities_from_docid(
                cursor, docid, 'entity_ids')

            # Create nodes for named entities
            # [['Washington Redskins', '[30]', '1', 'ORG']]
            for entity in entities:
                ent_name = entity[0]
                try:
                    ent_positions = json.loads(entity[1])
                except:
                    print(f'issue with enitity: {entity[1]}')
                    continue
                ent_tf = int(entity[2])
                ent_type = entity[3]

                graph.add_node(Node(ent_name, ent_type, ent_positions, ent_tf))

        # group 21 work
        first_par_terms = group21_utils.get_first_paragraph(index_utils, docid)
        
        
        # Retrieve top n tfidf terms from database.        
        if nr_terms > 0.0:
            terms = db_utils.get_entities_from_docid(
                cursor, docid, 'tfidf_terms')[:nr_terms]
         
            # Create nodes for tfidf terms
            for term in terms[:nr_terms]:  # [['Washington Redskins', '[30]', '1', 'ORG']]
                #term_positions is the index of the paragraphs in which the term occurs, first paragraph is index 3.
                #term_tf is the number of times the term occurs in the document
                
                term_name = term[0]
                term_positions = json.loads(term[1])
                term_tf = int(term[2])
                # if the term is in the first paragraph (index 3):
                #if 3 in term_positions:
                   #term_tf = first_par_terms.count(term_name)
                   #print("New term_tf:")
                   #print(term_tf)
                   # compute the number of times this word occurs in the first paragraph, assign this to term_tf
                graph.add_node(Node(term_name, 'term', term_positions, term_tf))
        """
        for term in first_par_terms:
           term_tf = first_par_terms.count(term)
           #print(term_tf)
           graph.add_node(Node(term, 'term', [3], term_tf))
        """
        # Determine node weighs
        N = graph.nr_nodes()
        n_stat = index_utils.stats()['documents'] # Number of documents |c|
        for node_name, node in graph.nodes.items():
            weight = 0.0
            if term_tfidf > 0:
                # computes tf_td
                tf = tf_func(node, N)

                if node.node_type == 'term':
                    # error here currently
                    df = index_utils.get_term_counts(
                        utils.clean_NE_term(node_name), analyzer=None)[0] + 1e-5
                    # computes W_td
                    weight += utils.tfidf(tf, df, n_stat)
                else:
                    weight += tf

            # by default NOT USED
            if term_position > 0:
                weight += term_position * \
                    position_in_text(node, docid, index_utils)

            node.weight = weight

        # Enity weights differ in magnitide from terms, since they are tf only (normalize both individually).
        equalize_term_and_entities(graph)

        embeddings_not_found = 0
        # Initialize edges + weights
        for node_key in graph.nodes.keys():
            for other_node_key in graph.nodes.keys():
                if node_key == other_node_key:
                    continue

                weight = 0.0
                if text_distance > 0:
                    distance = closest_distance(
                        graph.nodes[node_key], graph.nodes[other_node_key])
                    weight += text_distance * distance_in_text(distance)

                if term_embedding > 0:
                    weight += term_embedding * edge_embedding_weight(
                        graph.nodes[node_key], graph.nodes[other_node_key], embeddings, embeddings_not_found)

                if weight > 0.0:
                    graph.add_edge(node_key, other_node_key, weight)


def tf_func(node, N: int) -> float:
    if node.tf == 1:
        return 1 / N
    else:
        return (1 + np.log(node.tf-1)) / N


def position_in_text(node: Node, docid: str, index_utils) -> float:
    # location refers to the earliest paragraph index (starts at 0, so +1).
    return 1/(min(node.locations)+1)


def distance_in_text(distance: int) -> float:
    if distance <= 1:
        return 1/(1.0 + distance)
    else:
        return 0.0


def edge_embedding_weight(node_a, node_b, embeddings, embeddings_not_found):
    try:
        similarity = embeddings.similarity(node_a.__str__(), node_b.__str__())
    except:
        #print(f'Wd did not found: {node_a.__str__()}, {node_b.__str__()}')
        similarity = 0
    return similarity


def closest_distance(node_a, node_b):
    min_distance = 999999
    for locations in node_a.locations:
        for other_locations in node_b.locations:
            distance = abs(locations-other_locations)
            if distance < min_distance:
                min_distance = distance
    return min_distance


def equalize_term_and_entities(graph):
    """Normalize NE weights and tf-idf weights to obtain comparable weight."""
    term_weights = {'dummy0000': 0.0}
    entity_weights = {'dummy0000': 0.0}

    for node in graph.nodes.values():
        if node.node_type == 'term':
            term_weights[node] = node.weight
        else:
            entity_weights[node] = node.weight

    normalized_term_weights = utils.normalize_dict(term_weights)
    normalized_entity_weights = utils.normalize_dict(entity_weights)

    del normalized_term_weights['dummy0000']
    del normalized_entity_weights['dummy0000']

    for node in graph.nodes.values():
        if node.node_type == 'term':
            node.weight = normalized_term_weights[node]
        else:
            node.weight = normalized_entity_weights[node]
