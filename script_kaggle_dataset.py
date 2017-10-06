import json
import numpy as np
import copy
import xlsxwriter
import matplotlib.pyplot as plt
import os
import sys


FOLDER_KAGGLE = 'kaggle2/'

#### DEFINE CONSTRAIN HERE ###
MINLEN = 0.0 # duration
MAXLEN = 30.0 
MIN_INSTANCES = 40 # instance of sound per category


# this the result of the mapping from FS sounds to ASO
try:
    with open(FOLDER_KAGGLE + 'json/FS_sounds_ASO_postIQA.json') as data_file:
        data_duration = json.load(data_file)
except:
    raise Exception('CHOOSE A MAPPING FILE AND ADD IT TO ' + FOLDER_KAGGLE +'json/ FOLDER (THE FILE INCLUDE DURATION INFORMATION NEEDED)')

# load json with votes, to select only PP and PNP
try:
    with open(FOLDER_KAGGLE + 'json/votes_sounds_annotations.json') as data_file:
        data_votes = json.load(data_file)
except:
    raise Exception('ADD THE FILE CONTAINING THE VOTES (list of dict "value", "freesound_sound_id", "node_id") AND ADD IT TO THE FOLDER ' + FOLDER_KAGGLE +'json/')
    
try:
# load json with ontology, to map aso_ids to understandable category names
    with open(FOLDER_KAGGLE + 'json/ontology.json') as data_file:
         data_onto = json.load(data_file)
except:
    raise Exception('ADD AN ONTOLOGY JSON FILE TO THE FOLDER ' + FOLDER_KAGGLE +'json/')

    
# PP and PNP for sounds duration <= 20 and durantion >= 5
result = {o['id']:set() for o in data_onto}
# dict with all ASO_ids, every value initialized as an empty set

# GET ANNOTATIONS WITH VOTES 0.5 (PNP) or 1.0 (PP)
for v in data_votes:
    # apply duration filter
    if data_duration[str(v['freesound_sound_id'])]['duration']<=MAXLEN and data_duration[str(v['freesound_sound_id'])]['duration']>=MINLEN:
        # apply PRESENCE filter
        if v['value']>0.4:
            result[v['node_id']].add(v['freesound_sound_id'])
            
# process for removing duplicates with Present and non present votes:
for v in data_votes:
    if v['value']<0.1:
        if v['freesound_sound_id'] in result[v['node_id']]:
#            print v['freesound_sound_id'], v['node_id'], v['value']
            result[v['node_id']].remove(v['freesound_sound_id'])

print 'Number of categories with more than ' + str(MIN_INSTANCES) + ' sounds of duration [' + str(MINLEN) + ':' +\
      str(MAXLEN) + ']: ' + str(len([o for o in result if len(result[o]) >= MIN_INSTANCES]))

data_onto_by_id = {o['id']:o for o in data_onto}
result_leaves = {o:result[o] for o in result if len(data_onto_by_id[o]['child_ids'])<1}
print 'Number of leaf categories with more than ' + str(MIN_INSTANCES) + ' sounds of duration [' + str(MINLEN) + ':' +\
      str(MAXLEN) + ']: ' + str(len([o for o in result_leaves if len(result_leaves[o]) >= MIN_INSTANCES]))


# total amount of labels, over result_leaves
total_amount = 0
for key, value in result_leaves.iteritems():
    #candidate categories have more than MIN_INSTANCES samples
    if len(value) >= MIN_INSTANCES:
        total_amount += len(value)
        
print 'Total amount of labels in leaf categories with more than ' + str(MIN_INSTANCES) + ' samples of duration [' + str(MINLEN) + ':' +\
      str(MAXLEN) + '] (s): ' + str(total_amount) + ' labels'

# total amount of sounds, over result_leaves
all_ids = []
for key, value in result_leaves.iteritems():
    if len(value) >= MIN_INSTANCES:     #candidate categories have more than MIN_INSTANCES samples
        all_ids += value
all_ids = set(all_ids)

print 'Total amount of sounds in leaf categories with more than ' + str(MIN_INSTANCES) + ' samples of duration [' + str(MINLEN) + ':' +\
      str(MAXLEN) + '] (s): ' + str(len(all_ids)) + ' samples'


# --------------------- PRINT ALL CATEGORIES --------------------- #

### UTILS FUNCTIONS ###
def get_parents(aso_id, ontology):
    parents = []
    ontology_by_id = {o['id']:o for o in ontology}
    # 1st pass for direct parents
    for o in ontology:
        for id_child in o["child_ids"]:
            if id_child == aso_id:
                parents.append(o['id'])
    return [ontology_by_id[parent] for parent in parents]
        
def get_all_parents(aso_id, ontology): 
    """ 
    Recursive method to get the parents chain for an aso category
    """
    ontology_by_id = {o['id']:o for o in ontology}
    def paths(node_id, cur=list()):
        parents = get_parents(node_id, ontology)
        if not parents:
            yield cur
        else:
            for node in parents:
                for path in paths(node['id'], [node['name']] + cur):
                    yield path
    return paths(aso_id)

def sorted_occurrences_labels(result, ontology, min_samples):
    """
    Create the worksheet with the number of sounds in each category of the ASO 
    Arguments:  - result from previous stage, e.g. result_leaves
                - ontology from json file
                - minimum samples in a categor, e.g. MIN_INSTANCES
    """
    ontology_by_id = {o['id']:o for o in ontology}
    category_occurrences = []
    total_sounds = 0
    for node_id in result.keys():
        nb_sample = len(result[node_id])
        if nb_sample >= min_samples:
            total_sounds += nb_sample
            # get the names of parents (if several path, take one only and add (MULTIPLE PARENTS))
            all_parents = list(get_all_parents(node_id, ontology))
            if len(all_parents) > 1:
                names = ' > '.join(all_parents[0]+[ontology_by_id[node_id]['name']]) + ' (MULTIPLE PARENTS)'
            else:
                names = ' > '.join(all_parents[0]+[ontology_by_id[node_id]['name']])
            category_occurrences.append((names, node_id, nb_sample))
    category_occurrences = sorted(category_occurrences, key=lambda oc: oc[0])
    category_occurrences.append(('Total number of labels', '', total_sounds))
    category_occurrences.reverse()
    
    workbook = xlsxwriter.Workbook(FOLDER_KAGGLE + 'list_categories_dataset_draft.xlsx')
    worksheet = workbook.add_worksheet('list categories')
    
    for idx, obj in enumerate(category_occurrences):
        worksheet.write(idx, 0, obj[0])
        worksheet.write(idx, 1, obj[1])
        worksheet.write(idx, 2, obj[2])
#    print '\n'
#    print 'Audio Set categories with their number of audio samples:\n'
#    for i in category_occurrences:
#        print str(i[0]).ljust(105) + str(i[1])


### WRITE EXCEL FILE ###
sorted_occurrences_labels(result_leaves, data_onto, MIN_INSTANCES)

# --------------------------------------------------------------- #

# ------------------------ EXTRACT SOUNDS ----------------------- #

result_final = {node_id:result_leaves[node_id] for node_id in result_leaves 
                if len(result_leaves[node_id])>=MIN_INSTANCES}
sounds_with_labels = {sound_id:[] for sound_id in all_ids}
for node_id in result_final:
    for s in result_final[node_id]:
        sounds_with_labels[s].append(node_id)

# how many sounds with multiple labels
print 'Total amount of sounds with more than one label: {0} samples'.format(
    len([1 for sound_id in sounds_with_labels if 
         len(sounds_with_labels[sound_id])>1]))

print 'Total Number of sounds: {}'.format(len(sounds_with_labels))

# --------------------------------------------------------------- #

# ------------------------ CREATE FILES --------------------------#

# DATASET FILE (Category based)
sound_ids = sounds_with_labels.keys()
sound_ids.sort()
json.dump({node_id:list(result_final[node_id]) for node_id in result_final}, open(FOLDER_KAGGLE + 'dataset.json', 'w'), indent=4)

# ALL IDS (FOR FRED)
json.dump(sound_ids, open(FOLDER_KAGGLE + 'all_ids.json', 'w'))

# LICENSE FILE
# (WARNING, DEMENDS A LOT OF MEMORY):

import manager
c = manager.Client(False)
b = c.load_basket_pickle('freesound_db_160317.pkl')
id_to_idx = {b.ids[idx]:idx for idx in range(len(b))}

license_file = open(FOLDER_KAGGLE + 'licenses.txt', 'w')
license_file.write("This dataset uses the following sounds from Freesound:\n\n")
license_file.write("to access user page:  http://www.freesound.org/people/<username>\n")
license_file.write("to access sound page: http://www.freesound.org/people/<username>/sounds/<soundid>\n\n")
license_file.write("'<file name>' with ID <soundid> by <username> [<license>]\n\n")
for sound_id in sound_ids:
    sound = b.sounds[id_to_idx[sound_id]]
    name = sound.name.encode('utf-8').replace('\r', '')
    license_file.write("'{0}' of ID {1} by {2} [CC-{3}]\n"
                       .format(name, sound.id, sound.username, sound.license.split('/')[-3].upper()))
license_file.close()

# --------------------------------------------------------------- #

# ----------------------- SPLIT DEV EVAL -------------------------#
print '\n SPLIT \n'

# STRUCTURE DATA, SPLIT SINGLE/MULTIPLE LABELED SOUNDS
sounds_single = {s:sounds_with_labels[s] for s in sounds_with_labels if len(sounds_with_labels[s])==1}
sounds_multiple = {s:sounds_with_labels[s] for s in sounds_with_labels if len(sounds_with_labels[s])>1}

data_single = {r:[] for r in result_final}
for s in sounds_single:
    data_single[sounds_single[s][0]].append(s)

print 'Number of single labeled sounds: {0}'.format(len(sounds_single))
    
data_multiple = {r:[] for r in result_final}
for s in sounds_multiple:
    for i in sounds_multiple[s]: 
        data_multiple[i].append(s)

print 'Number of multi-labeled sounds: {0}'.format(len(sounds_multiple))

# ORDER BY DURATION

#c = manager.Client(False)
#b = c.load_basket_pickle('freesound_db_160317.pkl')
#id_to_idx = {b.ids[idx]:idx for idx in range(len(b))}

data_single_dur = {r:sorted([(s, b.sounds[id_to_idx[s]].duration) for s in data_single[r]], key=lambda c:c[1]) for r in data_single}
data_multiple_dur = {r:sorted([(s, b.sounds[id_to_idx[s]].duration) for s in data_multiple[r]], key=lambda c:c[1]) for r in data_multiple}

# SPLIT DEV/EVAL FOR SINGLE LABELED WITH RATIO 7:3 BASED ON DURATION
rule32 = ['dev', 'eval', 'dev', 'eval', 'dev']
rule73 = ['dev', 'eval', 'dev', 'dev', 'eval', 'dev', 'dev', 'eval', 'dev', 'dev']
data_single_dev = {r:[] for r in data_single_dur}
data_single_eval = {r:[] for r in data_single_dur}
for r in data_single_dur:
    for idx, s in enumerate(data_single_dur[r]):
        if rule73[idx%len(rule73)] == 'dev':
            data_single_dev[r].append(s[0])
        elif rule73[idx%len(rule73)] == 'eval':
            data_single_eval[r].append(s[0])
            
# RANDOMLY ADDING MULTIPLE LABELED WITH RATIO 7:3
data_dev = data_single_dev
data_eval = data_single_eval
for idx, s in enumerate(sounds_multiple):
    if rule73[idx%len(rule73)] == 'dev':
        for node_id in sounds_multiple[s]:
            data_dev[node_id].append(s)
    elif rule73[idx%len(rule73)] == 'eval':
        for node_id in sounds_multiple[s]:
            data_eval[node_id].append(s)

# EXPORT DATASET
ontology_by_id = {o['id']:o for o in data_onto}
dataset_dev = [{'name': ontology_by_id[node_id]['name'], 
                'audioset_id': node_id,
                'sound_ids': data_dev[node_id],
               } for node_id in data_dev]
dataset_eval = [{'name': ontology_by_id[node_id]['name'], 
                'audioset_id': node_id,
                'sound_ids': data_eval[node_id],
               } for node_id in data_eval]


# GET SOME STATS
ids_vote = {v['freesound_sound_id']:{} for v in data_votes if v['freesound_sound_id'] in all_ids}
for v in data_votes:
    if v['freesound_sound_id'] in all_ids:
        ids_vote[v['freesound_sound_id']][v['node_id']] = v

for cat in dataset_dev:
    cat['nb_sounds'] = len(cat['sound_ids'])
    cat['total_duration'] = sum([b.sounds[id_to_idx[id]].duration for id in cat['sound_ids']])
    cat['nb_users'] = len(set([b.sounds[id_to_idx[id]].username for id in cat['sound_ids']]))
    cat['nb_PP'] = len([id for id in cat['sound_ids'] if cat['audioset_id'] in ids_vote[id].keys() if ids_vote[id][cat['audioset_id']]['value']==1.0])
    cat['nb_PNP'] = len([id for id in cat['sound_ids'] if cat['audioset_id'] in ids_vote[id].keys() if ids_vote[id][cat['audioset_id']]['value']==0.5])
    
for cat in dataset_eval:
    cat['nb_sounds'] = len(cat['sound_ids'])
    cat['total_duration'] = sum([b.sounds[id_to_idx[id]].duration for id in cat['sound_ids']])
    cat['nb_users'] = len(set([b.sounds[id_to_idx[id]].username for id in cat['sound_ids']]))
    cat['nb_PP'] = len([id for id in cat['sound_ids'] if cat['audioset_id'] in ids_vote[id].keys() if ids_vote[id][cat['audioset_id']]['value']==1.0])
    cat['nb_PNP'] = len([id for id in cat['sound_ids'] if cat['audioset_id'] in ids_vote[id].keys() if ids_vote[id][cat['audioset_id']]['value']==0.5])
    
json.dump(dataset_dev, open(FOLDER_KAGGLE + 'dataset_dev.json', 'w'), indent=4)
json.dump(dataset_eval, open(FOLDER_KAGGLE + 'dataset_eval.json', 'w'), indent=4)


# PRINT INFO
#for cat in dataset_dev:
#    print cat['name'].ljust(40) + str(round(cat['total_duration'],2)).ljust(9) + str(cat['nb_PP']).ljust(10) + str(cat['nb_PNP'])
print '\n\n'
print 'CATEGORY dev // eval'.ljust(40) + 'DURATION'.ljust(16) + ' // ' + 'PP'.ljust(10) + ' // ' + 'PNP'.ljust(10) + ' // ' + 'USERS'
for idx in range(len(dataset_dev)):
    print dataset_dev[idx]['name'].ljust(40) + str(round(dataset_dev[idx]['total_duration'],2)).ljust(8) + ' ' +str(round(dataset_eval[idx]['total_duration'],2)).ljust(8) + ' // ' +  str(dataset_dev[idx]['nb_PP']).ljust(5) +' ' + str(dataset_eval[idx]['nb_PP']).ljust(5) + ' // ' + str(dataset_dev[idx]['nb_PNP']).ljust(5) + ' ' + str(dataset_eval[idx]['nb_PNP']).ljust(5) + ' // ' +  str(dataset_dev[idx]['nb_users']).ljust(5) + ' ' + str(dataset_eval[idx]['nb_users'])

# SANITY CHECK
for d in dataset_dev:
    if d['nb_sounds'] != d['nb_PP'] + d['nb_PNP']:
        print '\n PROBLEM IN DATASET DEV SPLIT!!! Category of ID {0} does not sum its PP and PNP annotations with number of sounds'.format(d['audioset_id'])

for d in dataset_eval:
    if d['nb_sounds'] != d['nb_PP'] + d['nb_PNP']:
        print '\n PROBLEM IN DATASET EVAL SPLIT!!! Category of ID {0} does not sum its PP and PNP annotations with number of sounds'.format(d['audioset_id'])

        
# --------------------------------------------------------------- #

# -------------------- REMOVE SOME CATEGORIES ------------------- #

print '\n FILTER CATEGORIES'

dataset_dev = json.load(open(FOLDER_KAGGLE + 'dataset_dev.json', 'rb'))
dataset_eval = json.load(open(FOLDER_KAGGLE + 'dataset_eval.json', 'rb'))

# Music > Music mood > Scary music
# Sounds of things > Vehicle > Motor vehicle (road) > Car > Car passing by ...
category_id_to_remove = set(['/t/dd00134', '/m/0c1dj', '/m/01vfsf', '/m/05jcn', '/m/09dsr', '/m/01gp74', '/m/05xp3j', '/m/021wwz', '/m/03r5q_', '/t/dd00037', '/m/0174nj'])

dataset_dev_filter = [d for d in dataset_dev if d['audioset_id'] not in category_id_to_remove]
dataset_eval_filter = [d for d in dataset_eval if d['audioset_id'] not in category_id_to_remove]

nb_labels_left = sum([d['nb_sounds'] for d in dataset_dev_filter] + [d['nb_sounds'] for d in dataset_eval_filter])

print 'Number of categories left: {0}'.format(len(dataset_dev_filter))

print 'Number of labels left: {0}'.format(nb_labels_left)

sounds_left = []
for idx in range(len(dataset_dev_filter)):
    sounds_left += dataset_dev_filter[idx]['sound_ids']
    sounds_left += dataset_eval_filter[idx]['sound_ids']
    
print 'Number of sounds left: {0}'.format(len(set(sounds_left)))

json.dump(dataset_dev_filter, open(FOLDER_KAGGLE + 'dataset_dev_filter.json', 'w'))
json.dump(dataset_eval_filter, open(FOLDER_KAGGLE + 'dataset_eval_filter.json', 'w'))

# --------------------------------------------------------------- #

# ---------------------- SPLIT LICENSE FILES -------------------- #

dataset_dev = json.load(open(FOLDER_KAGGLE + 'dataset_dev_filter.json', 'rb'))
dataset_eval = json.load(open(FOLDER_KAGGLE + 'dataset_eval_filter.json', 'rb'))
sound_ids_dev = set()
sound_ids_eval = set()
for category in dataset_dev:
    sound_ids_dev.update(category['sound_ids'])
for category in dataset_eval:
    sound_ids_eval.update(category['sound_ids'])
sound_ids_dev = list(sound_ids_dev)  
sound_ids_eval = list(sound_ids_eval)
sound_ids_dev.sort()
sound_ids_eval.sort()

#import manager
#c = manager.Client(False)
#b = c.load_basket_pickle('freesound_db_160317.pkl')
#id_to_idx = {b.ids[idx]:idx for idx in range(len(b))}
license_file = open(FOLDER_KAGGLE + 'licenses_dev.txt', 'w')
license_file.write("This dataset uses the following sounds from Freesound:\n\n")
license_file.write("to access user page:  http://www.freesound.org/people/<username>\n")
license_file.write("to access sound page: http://www.freesound.org/people/<username>/sounds/<soundid>\n\n")
license_file.write("'<file name>' with ID <soundid> by <username> [<license>]\n\n")
for sound_id in sound_ids_dev:
    sound = b.sounds[id_to_idx[sound_id]]
    name = sound.name.encode('utf-8').replace('\r', '')
    license_file.write("'{0}' of ID {1} by {2} [CC-{3}]\n"
                       .format(name, sound.id, sound.username, sound.license.split('/')[-3].upper()))
license_file.close()

license_file = open(FOLDER_KAGGLE + 'licenses_eval.txt', 'w')
license_file.write("This dataset uses the following sounds from Freesound:\n\n")
license_file.write("to access user page:  http://www.freesound.org/people/<username>\n")
license_file.write("to access sound page: http://www.freesound.org/people/<username>/sounds/<soundid>\n\n")
license_file.write("'<file name>' with ID <soundid> by <username> [<license>]\n\n")
for sound_id in sound_ids_eval:
    sound = b.sounds[id_to_idx[sound_id]]
    name = sound.name.encode('utf-8').replace('\r', '')
    license_file.write("'{0}' of ID {1} by {2} [CC-{3}]\n"
                       .format(name, sound.id, sound.username, sound.license.split('/')[-3].upper()))
license_file.close()

# --------------------------------------------------------------- #

# -------------------------- CREATE CSV ------------------------- #
dataset_dev = json.load(open(FOLDER_KAGGLE + 'dataset_dev_filter.json', 'rb'))
dataset_eval = json.load(open(FOLDER_KAGGLE + 'dataset_eval_filter.json', 'rb'))

try:
    merge = json.load(open(FOLDER_KAGGLE + 'merge_categories.json', 'rb'))
except:
    raise Exception('CREATE THE FILE "merge_categories.json" for Task2')
node_id_parent = {}
for d in merge:
    for dd in merge[d]:
        node_id_parent[dd] = d
        
#ontology = json.load(open('ontology/ontology.json', 'rb'))
#ontology_by_id = {o['id']:o for o in ontology}

import csv
with open(FOLDER_KAGGLE + 'dataset_dev.csv', 'wb') as f:
    writer = csv.writer(f, delimiter='\t', escapechar='', quoting=csv.QUOTE_NONE)
    for d in dataset_dev:
        for sound_id in d['sound_ids']:
            try:
                writer.writerow([sound_id, d['audioset_id'], d['name'], node_id_parent[d['audioset_id']], ontology_by_id[node_id_parent[d['audioset_id']]]['name']])
            except:
                writer.writerow([sound_id, d['audioset_id'], d['name'], None, None])

with open(FOLDER_KAGGLE + 'dataset_eval.csv', 'wb') as f:
    writer = csv.writer(f, delimiter='\t', escapechar='', quoting=csv.QUOTE_NONE)
    for d in dataset_eval:
        for sound_id in d['sound_ids']:
            try:
                writer.writerow([sound_id, d['audioset_id'], d['name'], node_id_parent[d['audioset_id']], ontology_by_id[node_id_parent[d['audioset_id']]]['name']])
            except:
                writer.writerow([sound_id, d['audioset_id'], d['name'], None, None])

                
# --------------------------------------------------------------- #

