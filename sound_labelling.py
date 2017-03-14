import json
import manager
from nltk.stem.porter import PorterStemmer
import copy


# stem and lower case of fs tags in Audio Set Ontology:
def preproc_ontology(ontology):
    stemmer = PorterStemmer()
    ontology_stem = copy.deepcopy(ontology)
    for idx, category in enumerate(ontology):
        ontology_stem[idx]["fs_tags"] = []
        for t in category["fs_tags"]:
            if isinstance(t, unicode):
                t_stem = stemmer.stem(t.lower())
                ontology_stem[idx]["fs_tags"].append(t_stem)
            elif isinstance(t, list):
                t_stem = [stemmer.stem(i.lower()) for i in t]
                ontology_stem[idx]["fs_tags"].append(t_stem)
    return ontology_stem
            
# process sound auto-labelling 
def auto_label(basket, ontology):
    """
    Add attributes aso_labels and aso_ids in basket sounds
    """
    Bar = manager.ProgressBar(len(b), 30, 'Linking...')
    Bar.update(0)
    for idx, sound in enumerate(basket.sounds):
        Bar.update(idx+1)
        sound.aso_labels = []
        sound.aso_ids = []
        for category in ontology:
            is_from_category = False
            for t in category["fs_tags"]:
                if isinstance(t, unicode):
                    if t in sound.tags:
                        is_from_category = True
                elif isinstance(t, list):
                    if set(t).issubset(set(sound.tags)):
                        is_from_category = True
            if is_from_category:
                sound.aso_labels.append(category["name"])
                sound.aso_ids.append(category["id"])
    return basket

def calculate_occurrences_aso_categories(basket, ontology_by_id):
    """
    Returns a dict {"<ASO_id>": [nb_occcurrences, [fs_id, ...]], ...}
    """
    aso_category_occurrences = {key:[0, []] for key in ontology_by_id.keys()} 
    Bar = manager.ProgressBar(len(basket), 30, 'Counting')
    Bar.update(0)
    for idx, sound in enumerate(basket.sounds):
        Bar.update(idx+1)
        for aso_id in sound.aso_ids:
            aso_category_occurrences[aso_id][0] += 1
            aso_category_occurrences[aso_id][1].append(sound.id)
    return aso_category_occurrences
    
def display_occurrences_labels(occurrences):
    print '\n'
    print 'Audio Set labels occurrences:\n'
    for i in occurrences.keys():
        print str(ontology_by_id[i]["name"]).ljust(30) + str(occurrences[i][0])

    
if __name__ == '__main__':
    c = manager.Client(False)
    b = c.load_basket_pickle('freesound_db_030317.pkl')
    ontology = json.load(open('ontology_nature.json','rb'))
    ontology_by_id = {o['id']:o for o in ontology}
    b.text_preprocessing() # stem and lower case for tags in freesound basket
    ontology_stem = preproc_ontology(ontology)
    b = auto_label(b, ontology_stem)
    aso_category_occurrences = calculate_occurrences_aso_categories(b, ontology_by_id)
    display_occurrences_labels(aso_category_occurrences)
    