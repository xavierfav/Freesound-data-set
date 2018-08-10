
import json
import copy
import json

MINLEN = 0.3  # duration
MAXLEN = 30.0

FOLDER_DATA = 'kaggle3/'

"""load initial data with votes, clip duration and ontology--------------------------------- """

# dict with the new 30k sounds from March17-July18, and metadata
# useful to get the duration of every sound and license
try:
    with open(FOLDER_DATA + 'json/FS_sounds_ASO_postIQA_only30k_1718.json') as data_file:
        data_mapping_only30k_1718 = json.load(data_file)
except:
    raise Exception(
        'CHOOSE A MAPPING FILE AND ADD IT TO ' + FOLDER_DATA + 'json/ FOLDER (THE FILE INCLUDE DURATION INFORMATION NEEDED)')

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
# Aug2: last dump before the addition:
# - of 30k new FSounds (last year) with original mapping +
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
    # Aug03 es justo despues de cargar los nuevos sounds en la platform, con el mapping original. 297291
    with open(FOLDER_DATA + 'json/votes_dumped_2018_Aug_03.json') as data_file:
        data_votes_raw = json.load(data_file)
except:
    raise Exception('ADD A DUMP JSON FILE OF THE FSD VOTES TO THE FOLDER ' + FOLDER_DATA + 'json/')

# data_votes_raw is a dict where every key is a cat
# the value of every cat is a dict, that contains 5 keys: PP, PNP, NP, U, candidates
# the corresponding values are a list of Freesound ids
#

# # this has information about the 396 valid categories, taken directly from the Django database
# try:
#     with open(FOLDER_DATA + 'json/valid_categories_FSD1_dict.json') as data_file:
#         data_info_valid = json.load(data_file)
# except:
#     raise Exception('ADD A DUMP JSON FILE OF THE FSD VOTES TO THE FOLDER ' + FOLDER_DATA + 'json/')
#
# # get hierarchy path for every category
# try:
#     with open(FOLDER_DATA + 'json/hierarchy_dict.json') as data_file:
#         hierarchy_dict = json.load(data_file)
# except:
#     raise Exception('ADD JSON FILE with the hierarchy paths for every class to the folder: ' + FOLDER_DATA + 'json/')

# get 41 classes from Kaggle2018
try:
    with open(FOLDER_DATA + 'json/data_eval.json') as data_file:
        data_eval41classes = json.load(data_file)
except:
    raise Exception('ADD JSON FILE with the 41 classes of FSDKaggle2018: ' + FOLDER_DATA + 'json/')



"""
*****************************************************************************BEGIN SCRIPT
"""

"""
# the goal is to add more candidates to some categories that do not have a lot.
some have enough to reach 1k, but in others we have less than one hundred candidates in the dataset.
To mitigate this, we search for new candidates and then we add them only in the less abundant classes.
Procedure:
# gather sounds in the 41 classes of Kaggle2018 that are not in data_mapping (ie they are new, unvoted, ie candidates)
# then, apply filters (need duration and license) to meet restrictions in FSDKaggle2018
# for simplicity, we do not populate, eg in Violin, we only consider candidates to Violin (and we do not care about pizzicato etc)
# then post-processing: in-domain multilabel, re
# these are the potential true candidates that could be added to FSDKaggle2018.
# save a json with them all (only 2.6k)
TODO: then we will decide which classes are more in need of them (not all of them will be needing them)
"""

# check data
new_ids = []
for key in data_mapping_only30k_1718.keys():
    new_ids.append(int(key))

print('Number of sounds not found in data_mapping; they must be new from last year (AFTER SET): %d' % len(new_ids))


# begin applying filters
# FILTER 1: Consider only 41 categories of FSDKaggle2018 AND the sounds that are new from the last year
# we assume that all the candidates that are new, have not been voted
# (we just made the dump minutes after they were in platform)
#
data_dev_LQ_new_41 = {}
for cat_id, groups in data_votes_raw.iteritems():
    if cat_id in data_eval41classes.keys():
        data_dev_LQ_new_41[cat_id] = []
        data_dev_LQ_new_41[cat_id] = [fs_id for fs_id in groups['candidates'] if fs_id in new_ids]


# FILTER 2: Apply duration filter: Within the 41 categories, keep sounds with durations [MINLEN: MAXLEN]
# create copy for result of filter
data_dev_LQ_new_41_d = copy.deepcopy(data_dev_LQ_new_41)
for catid, sound_ids in data_dev_LQ_new_41_d.iteritems():
    data_dev_LQ_new_41_d[catid] = []

for catid, sound_ids in data_dev_LQ_new_41.iteritems():
    for fsid in sound_ids:
        if (data_mapping_only30k_1718[str(fsid)]['duration'] <= MAXLEN) and \
                (data_mapping_only30k_1718[str(fsid)]['duration'] >= MINLEN):
            data_dev_LQ_new_41_d[catid].append(fsid)


# FILTER 2.1: NC license. Within the categories, discard sounds with NC licenses and sampling+
# create copy for result of filter
data_dev_LQ_new_41_dl = copy.deepcopy(data_dev_LQ_new_41_d)
for catid, groups in data_dev_LQ_new_41_dl.iteritems():
    data_dev_LQ_new_41_dl[catid] = []

for catid, sound_ids in data_dev_LQ_new_41_d.iteritems():
    for fsid in sound_ids:
        if data_mapping_only30k_1718[str(fsid)]['license'].split('/')[-3] != 'by-nc' and \
                        data_mapping_only30k_1718[str(fsid)]['license'].split('/')[-3] != 'sampling+':
            data_dev_LQ_new_41_dl[catid].append(fsid)


"""
POST PROCESSING STAGE
only inline multilabel analysis
"""
# report first
all_annotations = []
for catid, sound_ids in data_dev_LQ_new_41_dl.iteritems():
    all_annotations += sound_ids

print('\nNumber of candidate annotations: %d' % len(all_annotations))
# some are multilabel inline, get rid of them

# naturally, there can be multiple annotations for every sound
all_sound_ids = list(set(all_annotations))
print('Number of sounds: %d' % len(all_sound_ids))
# therefore, some of them are repeated, and will have to be removed (not only the repetetition but all the instances)

# difference is 270 items, this can mean:
# 270 sounds with 2 annotations
# or less sounds with more annotations each: eg, 135 sounds with 3 annotations

# --------------- REMOVE MULTIPLE LABELED SOUNDS ---------------- #
# --------------------------------------------------------------- #
# BEWARE this is ONLY IN DOMAIN, ie remove the sounds that happen to be in 2 classes within the set of 41
# --------------- REMOVE MULTIPLE LABELED SOUNDS ---------------- #

# all_annotations has all annotations together, ie all the ids belonging to all the classes
# some ids will be repeated as they belong to several categories, ie they have several labels.
sounds_to_remove = [s for s in all_annotations if all_annotations.count(s) > 1]
# beware: if it exists N times, it is counted N times
print("Sounds that will be removed from the total of %d: %d sounds" % (len(all_sound_ids), len(list(set(sounds_to_remove)))))

# proceed removing
data_dev_LQ_new_41_dl_single = copy.deepcopy(data_dev_LQ_new_41_dl)

for cat_id, sound_ids in data_dev_LQ_new_41_dl_single.iteritems():
    for s in sounds_to_remove:
        if s in sound_ids:
            sound_ids.remove(s)

# sounds with multiple labels are removed from ALL groups, so that they dont exist anymore in the dataset
# double check
all_annotations_single = []
for catid, sound_ids in data_dev_LQ_new_41_dl_single.iteritems():
    all_annotations_single += sound_ids

print('\n Finally, in the selected sample: number of candidate annotations: %d' % len(all_annotations_single))
# some are multilabel inline, get rid of them

# naturally, there can be multiple annotations for every sound
all_sound_ids_single = list(set(all_annotations_single))
print('Number of sounds: %d' % len(all_sound_ids_single))

# --------------------------------------------------------------- #


# here we have, for every category, the new sounds from March17/July18 that comply with restrictions of FSDKaggle2018
for idx, (cat_id, sound_ids) in enumerate(data_dev_LQ_new_41_dl_single.iteritems(), 1):
    print("%d - %-25s: sounds: %-3d" % (idx, data_onto_by_id[cat_id]['name'], len(sound_ids)))

# since they are 2.6k only, we store a json with all of them to fetch them from FS, and we decide what to do
# json.dump(data_dev_LQ_new_41_dl_single, open(FOLDER_DATA + '/new/data_dev_LQ_new.json', 'w'))


# Now, the goal is to add it to:
# -see which categories of FSDKaggle2018 need it (those that by themselves do not reach 1k (worst case)
# -select new candidates randomly until reaching 1k
# (i think they will have to be all of the new candidates for simplicity, and considering they are not that many)

# TODO we may create another json with *only* those to be added

# To send FF:
# then, json for the old candidates,
# and json for the new ones: data_dev_LQ_new

# compute them lists
with open(FOLDER_DATA + 'new/data_dev_LQ_extended_1000.json') as data_file:
    data_old = json.load(data_file)

all_fs_ids_old = []
for catid, sound_ids in data_old.iteritems():
    all_fs_ids_old += sound_ids
print(len(all_fs_ids_old))

all_fs_ids_new = []
for catid, sound_ids in data_dev_LQ_new_41_dl_single.iteritems():
    all_fs_ids_new += sound_ids
print(len(all_fs_ids_new))

# store this and send to FF
# json.dump(all_fs_ids_old, open(FOLDER_DATA + '/new/all_fs_ids_old.json', 'w'))
# json.dump(all_fs_ids_new, open(FOLDER_DATA + '/new/all_fs_ids_new.json', 'w'))

a=9



