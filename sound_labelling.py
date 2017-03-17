import json
import manager
from nltk.stem.porter import PorterStemmer
import copy
import webbrowser


# stem and lower case of fs tags in Audio Set Ontology:
def preproc_ontology(ontology):
    stemmer = PorterStemmer()
    ontology_stem = copy.deepcopy(ontology)
    for idx, category in enumerate(ontology):
        ontology_stem[idx]["fs_tags"] = []
        for t in category["fs_tags"]:
            if isinstance(t, unicode):
                if t != 'review': # for removing "review" tags - abigous
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
    Arguments:  - basket object of Freesound collection
                - ontology from ASO json file (list of dict)
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

def calculate_occurrences_aso_categories(basket, ontology):
    """
    Returns a dict {"<ASO_id>": [nb_occcurrences, [fs_id, ...]], ...}
    Arguments:  - basket object of Freesound collection
                - ontology from ASO json file (list of dict)
    """
    ontology_by_id = {o['id']:o for o in ontology}
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
    print 'Audio Set labels number of occurrences:\n'
    for i in occurrences.keys():
        print str(ontology_by_id[i]["name"]).ljust(40) + str(occurrences[i][0])

def get_number_of_labeled_sounds(basket):
    count = 0
    for sound in basket.sounds:
        if len(sound.aso_ids) > 0:
            count += 1
    return count
    
def sorted_occurrences_labels(occurrences, basket):
    """
    Print the number of sounds in each category of the ASO 
    Arguments:  - occurrences from calculate_occurrences_aso_categories()
                - basket object of Freesound collection
    """
    aso_oc = []
    for k in occurrences.keys():
        aso_oc.append((ontology_by_id[k]['name'],occurrences[k][0]))
    aso_oc = sorted(aso_oc, key=lambda oc: oc[1])
    aso_oc.append(('Ontology', get_number_of_labeled_sounds(basket)))
    aso_oc.reverse()
    print '\n'
    print 'Audio Set labels number of occurrences:\n'
    for i in aso_oc:
        print str(i[0]).ljust(40) + str(i[1])
        
def create_html_random_sounds_for_category(aso_category_occurrences, category_id, nb_sounds=10):
    """
    Create a html with Freesound sound embeds
    Select a random set of sounds for the ASO category
    Arguments:  - occurrences from calculate_occurrences_aso_categories()
                - category id from ASO
                - number of sounds
    """
    sounds = aso_category_occurrences[category_id][1]
    # if the category has no sounds
    if len(sounds) < 1:
        print 'no sound in this category'
        return None
    # random selection of sounds
    selected_sounds = []
    for k in range(nb_sounds):
        random_id = random.randint(0,len(sounds)-1)
        selected_sounds.append(sounds[random_id])
        del sounds[random_id]
    # This list contains the begining and the end of the embed
    # Need to insert the id of the sound
    embed_blocks = ['<iframe frameborder="0" scrolling="no" src="https://www.freesound.org/embed/sound/iframe/', '/simple/medium/" width="481" height="86"></iframe>']
    # Create the html string
    message = """
    <html>
        <head></head>
        <body>
    """
    for idx in selected_sounds:
        message += embed_blocks[0] + str(idx) + embed_blocks[1]
    message += """
        </body>
    </html>
    """
    # Create the file
    f = open('category_'+ str(ontology_by_id[category_id]['name']) +'.html', 'w')
    f.write(message)
    f.close()
    # Open it im the browser
    webbrowser.open_new_tab('category_'+ str(ontology_by_id[category_id]['name']) +'.html')

def create_json_Fred(basket, name):
    """
    Create the json containing the data needed by Fred
    Arguments:  - a basket object (allready labeled...)
                - name of the file
    
    """
    b_dict = {}
    for s in basket.sounds:
        b_dict[s.id] = {'name':s.name, 'tags':s.tags, 'aso_ids':s.aso_ids, 'license':s.license, 'username':s.username, 'description':s.description, 'previews':s.previews.preview_hq_ogg, 'duration':s.duration}
    json.dump(b_dict, open(name+'+.json','w'))

def plot_histogram_nb_of_labels_sounds(basket):
    hist_labels = []
    for s in basket.sounds:
        hist_labels.append(len(s.aso_labels))
    plt.hist(hist_labels, bins=np.arange(np.array(hist_labels).min(), np.array(hist_labels).max()))
    plt.title('Histogram number of ASO labels in Freesound sounds')
    plt.xlabel("Value")
    plt.ylabel("Frequency")
    plt.show()
    
def get_list_FS_tags_in_ASO(ontology):
    pre_tags = []
    for o in ontology:
        pre_tags += o["fs_tags"]
    tags = []
    for t in pre_tags:
        if isinstance(t, unicode):
            tag.append(t)
        elif isinstance(t, list):
            tag += t
    tags = list(set(tags))
    return tags

def get_aso_class_fs_sound_id_dict(ontology, basket):
    """
    Returns a dict {"<aso_class>": [<fs_ids>, ...]}
    Arguments:  - ontology from ASO json file (list of dict)
                - basket object of Freesound collection
    """
    aso_class_fs_id_dict = {o['id']:[] for o in ontology}
    for sound in basket.sounds:
        for idx in sound.aso_ids:
            aso_class_fs_id_dict[idx].append(sound.id)
    return aso_class_fs_id_dict
    
def get_parents_dict(ontology):
    """
    Returns a dict {"<aso_class>": [<all_parent_classes>, ...]}
    Argument: Ontology from ASO json file (list of dict)
    """
    dict_direct_parent = {o['id']:[] for o in ontology}
    # 1st pass for direct parents
    for o in ontology:
        for id_child in o["child_ids"]:
            dict_direct_parent[id_child].append(o['id'])
    # loop to get all parent nodes
    dict_parents = dict_direct_parent
    for _ in range(6):
        dict_parents = _iterate_population(dict_direct_parent, dict_parents)
    return dict_parents
                
def _iterate_population(dict_direct_parents, dict_parents):
    new_dict = dict_parents
    for aso_id in dict_direct_parents.keys():
        for parent_id in dict_parents[aso_id]:
            for parend_id_candidate in dict_direct_parents[parent_id]:
                if parend_id_candidate not in dict_parents[aso_id]:
                    new_dict[aso_id].append(parend_id_candidate)
    return new_dict

def show_parents(aso_id, parents_dict):
    """ 
    Print parents of a class
    Arguments:  - an Audio Set Ontology ID
                - the parent_dict returned by get_parents_dict()
    """
    print ontology_by_id[aso_id]['name']
    for i in parents_dict[aso_id]:
        print ontology_by_id[i]['name']

def populate_aso_class(ontology, dict_parents, basket):
    """
    Add parent ASO classes to Freesound sounds in the basket
    Arguments:  - ontology from ASO json file (list of dict)
                - the parent_dict returned by get_parents_dict()
                - basket object of Freesound collection
    """
    ontology_by_id = {o['id']:o for o in ontology}
    new_basket = copy.deepcopy(basket)
    for idx, sound in enumerate(basket.sounds):
        for aso_id in sound.aso_ids:
            new_basket.sounds[idx].aso_ids += dict_parents[aso_id]
        new_basket.sounds[idx].aso_ids = list(set(new_basket.sounds[idx].aso_ids))
        new_basket.sounds[idx].aso_labels = [ontology_by_id[a]['name'] for a in new_basket.sounds[idx].aso_ids]
    return new_basket
    
if __name__ == '__main__':
    c = manager.Client(False)
    b = c.load_basket_pickle('freesound_db_160317.pkl')
    ontology = json.load(open('ontology_to_process2.json','rb'))
    ontology_by_id = {o['id']:o for o in ontology}
    b.text_preprocessing() # stem and lower case for tags in freesound basket
    ontology_stem = preproc_ontology(ontology)
    b = auto_label(b, ontology_stem)
    parents_dict = get_parents_dict(ontology)
    b_pupulated = populate_aso_class(ontology, parents_dict, b) 
    aso_category_occurrences = calculate_occurrences_aso_categories(b_pupulated, ontology)
    sorted_occurrences_labels(aso_category_occurrences, b_pupulated)
    