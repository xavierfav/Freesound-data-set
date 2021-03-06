
import json
import freesound
import copy


FOLDER_DATA = 'kaggle3/'

"""load initial data with votes, clip duration and ontology--------------------------------- """

# this the result of the mapping from FS sounds to ASO.
# a dict with 268k keys (the fs_ids) and values include metadata for every sound)
# 268k sounds with basic metadata and their corresponding ASO id.
# useful to get the duration of every sound
try:
    with open(FOLDER_DATA + 'json/FS_sounds_ASO_postIQA.json') as data_file:
        data_mapping = json.load(data_file)
except:
    raise Exception(
        'CHOOSE A MAPPING FILE AND ADD IT TO ' + FOLDER_DATA + 'json/ FOLDER (THE FILE INCLUDE DURATION INFORMATION NEEDED)')

# UPDATE: this does not contain the sounds added on August 3rd.
# We need to get this info
# for every id that is in data_votes_raw and is not in data_mapping (ie los 30k nuevos que se cargaron con el new mapping),
# retrieve duration with FS API
# los otros 40k old no aparecen porque no tienen candidates annotations. luego estan en platform, pero no en dump.
# done in script aside. if it takes too long, ask FF.


try:
    # load json with ontology, to map aso_ids to understandable category names
    with open(FOLDER_DATA + 'json/ontology.json') as data_file:
        data_onto = json.load(data_file)
except:
    raise Exception('ADD AN ONTOLOGY JSON FILE TO THE FOLDER ' + FOLDER_DATA + 'json/')

# data_onto is a list of dictionaries
# to retrieve them by id: for every dict o, we create another dict where key = o['id'] and value is o
data_onto_by_id = {o['id']: o for o in data_onto}
data_onto_by_name = {o['name']: o for o in data_onto}

# NOTE:
# Aug2: last dump before the addition of:
# - 30k new FSounds (last year) with original mapping +
# - 40k (old sounds that were never included in the original mapping)
# Aug3: dump right after that

try:
    # from March1, in the dumps we include only the trustable votes  (verification clips are met)
    # with open(FOLDER_DATA + 'json/votes_dumped_2018_May_16.json') as data_file:
    # with open(FOLDER_DATA + 'json/votes_dumped_2018_Jun_18.json') as data_file:
    # with open(FOLDER_DATA + 'json/votes_dumped_2018_Jun_22.json') as data_file:
    # with open(FOLDER_DATA + 'json/votes_dumped_2018_Jun_25.json') as data_file:
    # with open(FOLDER_DATA + 'json/votes_dumped_2018_Aug2.json') as data_file:

    # Aug2 es el dump ANTES de cargar cosas nuevas en la platform.
    with open(FOLDER_DATA + 'json/votes_dumped_2018_Aug_07.json') as data_file:
        data_votes_raw = json.load(data_file)
except:
    raise Exception('ADD A DUMP JSON FILE OF THE FSD VOTES TO THE FOLDER ' + FOLDER_DATA + 'json/')

# data_votes_raw is a dict where every key is a cat
# the value of every cat is a dict, that contains 5 keys: PP, PNP, NP, U, candidates
# the corresponding values are a list of Freesound ids
#

# this has information about the 396 valid categories, taken directly from the Django database
try:
    with open(FOLDER_DATA + 'json/valid_categories_FSD1_dict.json') as data_file:
        data_info_valid = json.load(data_file)
except:
    raise Exception('ADD A DUMP JSON FILE OF THE FSD VOTES TO THE FOLDER ' + FOLDER_DATA + 'json/')

# get hierarchy path for every category
try:
    with open(FOLDER_DATA + 'json/hierarchy_dict.json') as data_file:
        hierarchy_dict = json.load(data_file)
except:
    raise Exception('ADD JSON FILE with the hierarchy paths for every class to the folder: ' + FOLDER_DATA + 'json/')



"""
*****************************************************************************FUNCTIONS
"""


# ver los usos de estas dos
def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


def query_freesound_by_id(list_ids):
    """ Query Freesound by chunk of 150 sounds
        Retrieves only id of sounds """
    client = freesound.FreesoundClient()
    client.set_token("eaa4f46407adf86c35c5d5796fd6ea8b05515dca", "token")
    results = []
    for sub_list_ids in chunks(list_ids, 150):
        filter_str = 'id:(' + ' OR '.join([str(i) for i in sub_list_ids]) + ')'
        # page_result = client.text_search(query="", fields="id,pack,pack_name", page_size=50, filter=filter_str)
        page_result = client.text_search(query="", fields="id,duration,license,username,tags,name", page_size=150, filter=filter_str)
        results += [s for s in page_result]
    return results


"""
*****************************************************************************BEGIN SCRIPT
"""

# create list of ids that are not in data_mapping (because they are new)
list_ids_lack_info = []

# data_mapping.keys() returns unicode fs_ids: convert to int to compare in this format (much faster than unicode)
current_ids = [int(id) for id in data_mapping.keys()]

# go through candidates of every category: are they in data_mapping? else to_list
for idx, (cat_id, groups) in enumerate(data_votes_raw.iteritems(), 1):
    list_tmp_noduration = [fs_id for fs_id in groups['candidates'] if fs_id not in current_ids]
    print("%d - %-25s: new sounds: %-3d" % (idx, data_onto_by_id[cat_id]['name'], len(list_tmp_noduration)))
    list_ids_lack_info += list_tmp_noduration
    # if idx == 5:
    #     break

print('Number of candidate annotations not found in data_mapping; they must be new from last year (BEFORE SET): %d' % len(list_ids_lack_info))

# naturally, there can be multiple annotations for every sound
list_ids_lack_info_set = list(set(list_ids_lack_info))
print('Number of sounds not found in data_mapping; they must be new from last year (AFTER SET): %d' % len(list_ids_lack_info_set))


"""
***************************************************************************retrieve info for sounds that do not have it
"""

# instead of making a request for every id, lets optimize it
list_sound_objects = query_freesound_by_id(list_ids_lack_info_set)

print('\nNumber of sound objects retrieved from FS: %d out of %d' % (len(list_sound_objects), len(list_ids_lack_info_set)))

# any problem retrieving info from FS?
unaccesible_sound_ids = list(set(list_ids_lack_info_set) - set([s.id for s in list_sound_objects]))
if len(unaccesible_sound_ids) > 0:
    print('\nWe could not get info in %d sound(s)' % len(unaccesible_sound_ids))
    print('List of ids without FS info:')
    print(unaccesible_sound_ids)

# create dict with the new sounds and their metadata
data_mapping_only30k_1718 = {}

for s in list_sound_objects:
    data_mapping_only30k_1718[str(s.id)] = {}
    data_mapping_only30k_1718[str(s.id)]['duration'] = s.duration
    data_mapping_only30k_1718[str(s.id)]['license'] = s.license
    data_mapping_only30k_1718[str(s.id)]['username'] = s.username
    data_mapping_only30k_1718[str(s.id)]['tags'] = s.tags
    data_mapping_only30k_1718[str(s.id)]['name'] = s.name


if len(unaccesible_sound_ids) > 0:
    # dos sonidos deleted from Freesound: Fred had the info
    data_mapping_only30k_1718[str(434155)] = {}
    data_mapping_only30k_1718[str(434155)]['duration'] = 17.18
    data_mapping_only30k_1718[str(434155)]['license'] = 'unknown'

    data_mapping_only30k_1718[str(434156)] = {}
    data_mapping_only30k_1718[str(434156)]['duration'] = 18.57
    data_mapping_only30k_1718[str(434156)]['license'] = 'unknown'

# save the dict with the new 30k sounds from March17-July18
json.dump(data_mapping_only30k_1718, open(FOLDER_DATA + '/json/FS_sounds_ASO_postIQA_only30k_1718.json', 'w'))

# Finnaly, merge with old data_mapping and save it in
# FS_sounds_ASO_postIQA_2018_Aug_08.json, to be loaded from script_current_state_FSD.py
data_mapping_updated = copy.deepcopy(data_mapping)
data_mapping_updated.update(data_mapping_only30k_1718)
json.dump(data_mapping_updated, open(FOLDER_DATA + '/json/FS_sounds_ASO_postIQA_2018_Aug_08.json', 'w'))
# 297291 files

if len(data_mapping_updated) != 297291:
    print("Error creating data_mapping_updated")

# NOTES:
# Number of sound objects retrieved from FS: 29028 out of 29030
# antes: 268261
# new: 29030
# en total: 297,291
# en web: 297291

# Number of candidate annotations not found in data_mapping; they must be new from last year (BEFORE SET): 85953
# Number of sounds not found in data_mapping; they must be new from last year (AFTER SET): 29030

a=9