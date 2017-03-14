import pickle
import json
import operator
from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords

# mapping tag to id in the cooccurrence matrix
tag_to_id = pickle.load(open('tag_to_idx_cooc_matrix.pkl','rb'))
id_to_tag = {v: k for k,v in tag_to_id.iteritems()}

# Sparse cooccurrence matrix of Freesound tags
tag_cooccurrences = pickle.load(open('tag_cooccurrences.pkl','rb'))

# Audio Set Ontology
ontology = json.load(open('ontology.json','rb'))
ontology_by_name = {o['name']:o for o in ontology}
ontology_by_id = {o['id']:o for o in ontology}

# MAPPING
ontology_tags = dict.fromkeys(ontology_by_id.keys())
"""
Fill the ontology_tags dict like that:
ontology_tags[<node id>] = [<list of tags>]
and then save the ontology:
save_json(ontology_tags, <name_file>)
"""

def save_json(ontology, name):
    json.dump(open(name, 'w'))

# stop words
stop = set(stopwords.words('english'))

# set Freesound tags
set_tags = set(tag_to_id.keys())

def get_synonyms_wn(term):
    """ 
    Returns a list of terms synonyms of the term entered as argument
    The first synset returned by wordnet is chosen
    Stop words are removed
    Terms that are not Freesound tags are removed
    Could be improved with Entity Linking (may fail when asking for ambigous terms, eg: 'fire')
    """
    lemmas = wn.synsets(term)[0].lemma_names() 
    list_terms = flat_list([l.split('_') for l in lemmas])
    return list(set([l for l in list_terms if (l not in stop and l in set_tags)]))
    
def flat_list(l):
    return [item for sublist in l for item in sublist]

def get_list_cooc_terms(term):
    """
    Returns a list of tuples [(idx, nb_occ) , ...]
    where idx is the index of a tag that cooccure with
          nb_occ is the number of time that the tag cooccures
    """
    idx = tag_to_id[term]
    term_cooccurrences = tag_cooccurrences[idx].A[0]
    nonzero = tag_cooccurrences[idx].nonzero()[1]
    terms = [(i, term_cooccurrences[i]) for i in nonzero]
    #terms.sort(key=operator.itemgetter(1), reverse=True)
    return terms

def get_relevant_tags(term, synonyms = False):
    term = term.lower()
    if synonyms:
        list_syn = get_synonyms_wn(term)
    else:
        list_syn = [term]
    relevant_tags_id = []
    for t in list_syn:
        relevant_tags_id += get_list_cooc_terms(t)
    relevant_tags_id.sort(key=operator.itemgetter(1), reverse=True)
    relevant_tags = [id_to_tag[tag[0]] for tag in relevant_tags_id]
    return remove_duplicates(relevant_tags)

def remove_duplicates(mylist):
    return [v for (i,v) in enumerate(mylist) if v not in mylist[0:i]]

