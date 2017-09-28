
import json
import numpy as np
import copy
import xlsxwriter
import matplotlib.pyplot as plt
import os
import sys



# .json
# .json


# load json with durations for duration constraint
# this the result of the mapping from FS sounds to ASO
with open('Sept2017/FS_sounds_ASO_postIQA.json') as data_file:
    data_duration = json.load(data_file)


# data_duration is a dict with 268261 keys
# every key is a sound id from FS, that has been mapped to the ASO. In total, we have mapped 268261 from FS to the onto
# data_duration['228055']
# print data_duration['228055']

# and as value, there is a dictionary with username, description, etc, and
# most importantly: duration and aso_ids
# data_duration['228055']['duration'], in seconds
# data_duration['228055']['aso_ids'], each samples can have several labels, ie, mapped to several classes
# but the type is always a list of ids




# load json with votes, to select only PP and PNP
with open('Sept2017/votes_sounds_annotations.json') as data_file:
        data_votes = json.load(data_file)

# data_votes is a list of 45767 elements, ie annotations that have been valdiated.
# HOWEVER, in the paper we say there are only
# 42,575. difference of 3k? because in the paper we refer to the 398 categories,
# leaving the rest out as explained, presenting few data
# each element is a dict with 4 keys.
# the most important ones are:
# 'freesound_sound_id': obvious
# 'node_id': aso_id
# 'value': the actual vote by a human annotator: 1 = PP ; 0.5 = PNP for the belonging of the sound to the ASO class,
# ie, the presence of the ASO class in the FS id, ie the validation of an annotation

# indexing list
# data_votes[0]
# data_votes[3456]['freesound_sound_id']



# load json with ontology, to map aso_ids to understandable category names
with open('Sept2017/ontology.json') as data_file:
         data_onto = json.load(data_file)




# -----------------------------------------------------------
# # define constants
# MINLEN = 3.0
# # MAXLEN = 20.0
# MAXLEN = 30.0
# # MIN_INSTANCES = 50
# MIN_INSTANCES = 40


#
#
# # select only sounds that meet the following requirements:*********************************************************
# # -their belonging to an ASO class has been manually validated as PP or PN?
# # -they present duration ranging from 5-20 seconds.
#
#
# data_votes_Present = list()
#
# for idx, vote in enumerate(data_votes):
#     # print value
#     # print vote['freesound_sound_id']
#     # print vote['node_id']
#     # print vote['value']
#     # print('-------------------------')
#
#     #  preserve PP and PNP; reject Not Present and Unsure.
#     if vote['value'] == 1.0 or vote['value'] == 0.5:
#         data_votes_Present.append(vote)
#
# # data_votes_Present is a list with all the annotations PP and PNP: 26683 in total
# # this is a hard constraint. not much we can do about this.
#
#
# print('---------------------------------------------------------------------------------------')
# print ('now, how many of those are eligible according to duration?')
# print('---------------------------------------------------------------------------------------')
#
#
# data_votes_Present_duration = list()
#
# for idx, vote in enumerate(data_votes_Present):
#     # print value
#     # print vote['freesound_sound_id']
#     # # check the duration of the sound with such and FS_id:
#     # # data_duration['228055']['duration'], in seconds
#     # print data_duration[str(vote['freesound_sound_id'])]['duration']
#     # print('-------------------------')
#
#     #  preserve from 5 to 20s; else reject
#     if data_duration[str(vote['freesound_sound_id'])]['duration'] >= MINLEN and\
#                     data_duration[str(vote['freesound_sound_id'])]['duration'] <= MAXLEN:
#         data_votes_Present_duration.append(vote)
#
# # data_votes_Present_duration is a list with all the annotations validated as PP and PNP,
# # but only of sounds in the range 5-20s
# # ONLY 8731 in total. This means 2/3 of the sounds are OUT this range!!!
#
# # However, this number is irregularly distributed among a number of categories.
# # it may be that one category has 70 and another 20 sounds.
# # we need to know how populated every category is
#
# dict_valid_cats = dict()
#
#
# for idx, vote in enumerate(data_votes_Present_duration):
#     # print vote['node_id']
#     # print vote['freesound_sound_id']
#
#     # if category already exists, as key in the dict
#     # append the freesound_id to the existing list
#     if str(vote['node_id']) in dict_valid_cats:
#         dict_valid_cats[str(vote['node_id'])]['freesound_sound_id'].append(vote['freesound_sound_id'])
#         dict_valid_cats[str(vote['node_id'])]['cat_size'] += 1
#
#     else:
#         # category is new in the dict
#         # define new key with the aso_id (ie a category),
#         # and the value is a dict, containing a list with all the sound_ids positive for such a category
#         # define size = 1 to keep track of the size in this same variable
#         # and include semantic name from ontology
#         for i in np.arange(len(data_onto)):
#             if vote['node_id'] == data_onto[i]['id']:
#                 cat_name = str(data_onto[i]['name'])
#                 break
#
#         dict_valid_cats[str(vote['node_id'])] = {'cat_name': cat_name, 'freesound_sound_id': [vote['freesound_sound_id']], 'cat_size':1}
#         # dict_valid_cats[str(vote['node_id'])] = {'freesound_sound_id': [vote['freesound_sound_id']]}
#
# # dict_valid_cats is a dict with as many keys as sound categories with at least one sound that:
# # -has presence of the sound category in it
# # -has a duration ranging 5-20s
# # the amount of categories is 473 categories
#
# # BUT, how many categories have more than MIN_INSTANCES sounds?
# # this will be the last hard constraint, after which we have to decide soft constraints.
#
# count_valid_cats_MIN_INSTANCES=0
# for key, value in dict_valid_cats.iteritems():
#     if value['cat_size'] >= MIN_INSTANCES:
#         # print value['cat_name']
#         # print value['cat_size']
#         # print value['freesound_sound_id']
#         count_valid_cats_MIN_INSTANCES += 1
#         # print ('--------------------------------------')
#
# print ('---how many categories have more than MIN_INSTANCES sounds?\n')
# print count_valid_cats_MIN_INSTANCES
#
# # only 24 categories have more than 50 sounds, with the criteria defined above.
#
#
#
#
# # sanity check:
# count_all_sounds=0
# cat_size_vector=list()
# for key, value in dict_valid_cats.iteritems():
#     count_all_sounds += value['cat_size']
#     # to plot
#     cat_size_vector.append(value['cat_size'])
#
#
# if count_all_sounds != len(data_votes_Present_duration):
#     print ('----things do not match')
# else:
#     print ('----calculus seems fine')


# plot*************************************************
# y = [3, 10, 7, 5, 3, 4.5, 6, 8.1]
# N = len(cat_size_vector)
# x = range(N)
# width = 1/1.5
# plt.bar(x, cat_size_vector, width, color="blue")
# plt.grid(True)
# plt.xlabel('categories')
# plt.ylabel('VALID sounds (after Presentness and duration filter')
# plt.show()
#
#
# plt.figure()
# plt.bar(x, np.sort(cat_size_vector), width, color="blue")
# plt.grid(True)
# plt.xlabel('categories')
# plt.ylabel('VALID sounds (after Presentness and duration filter)')
# plt.show()



# TO DO:
# are there duplicates within the same category?
# or sounds that are voted more than once and therefore appear more than once in a given category?
# this would worsen the situation even more

# however, this number is not final, as a scarce child can populate the parent

# Comments: please check this is ok. the number is VERY LOW, but it seems correct to me...
# If this is the case:
# -we started with 26683 PRESENT annotations. this is the real starting point. a bit higher than ISMIR paper,
# because in it, we stick to 398 categories.
# -this number is greatly reduced when the duration constraint is imposed (to 8731), ie 1/3 roughly
# -such an amount of sounds is irregularly distributed among the categories, a lot of categories with 10, 20 sounds.
# - only 24 categories exceed 50 examples.


# options:
# -relax the duration constraint to: 5-30 (not less than 5, cause it would not be tagging...)
# -relax the min number of sounds per class... if we demand 40, we get 31, still few.
# -less sounds than 40 is too few sounds....

# new trial: duration: 5-30 and MIN_INSTANCES=40
# after the duration filter we keep 11k, and in the end we get 61 categories...
# (still 15k sounds out of the range, where are they in duration)

# -we have to do an analysis of the categories that are out (more than 400) and see if they can populate parents
# probably this is the fastest way?
# else, annotate more
# how about target of 100 categories (nice number)



################# XF ######################
#
# define constants
MINLEN = 0.0
# MAXLEN = 20.0
MAXLEN = 30.0
# MIN_INSTANCES = 50
MIN_INSTANCES = 40

# PP and PNP for sounds duration <= 20 and durantion >= 5
result = {o['id']:set() for o in data_onto}
# dict with all ASO_ids, every value initialized as an empty set


for v in data_votes:
    # apply duration filter
    if data_duration[str(v['freesound_sound_id'])]['duration']<=MAXLEN and data_duration[str(v['freesound_sound_id'])]['duration']>=MINLEN:
        # apply PRESENCE filter
        if v['value']>0.4:
            result[v['node_id']].add(v['freesound_sound_id'])
print 'Number of categories with more than ' + str(MIN_INSTANCES) + ' sounds of duration [' + str(MINLEN) + ':' +\
      str(MAXLEN) + ']: ' + str(len([o for o in result if len(result[o]) >= MIN_INSTANCES]))

data_onto_by_id = {o['id']:o for o in data_onto}
result_leaves = {o:result[o] for o in result if len(data_onto_by_id[o]['child_ids'])<1}
print 'Number of leaf categories with more than ' + str(MIN_INSTANCES) + ' sounds of duration [' + str(MINLEN) + ':' +\
      str(MAXLEN) + ']: ' + str(len([o for o in result_leaves if len(result_leaves[o]) >= MIN_INSTANCES]))


# name, size


# total amount of labels, over result_leaves
total_amount = 0
for key, value in result_leaves.iteritems():
    if len(value) >= MIN_INSTANCES:     #candidate categories have more than MIN_INSTANCES samples
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
    
    workbook = xlsxwriter.Workbook('list_categories_dataset_draft.xlsx')
    worksheet = workbook.add_worksheet('list categories')
    
    for idx, obj in enumerate(category_occurrences):
        worksheet.write(idx, 0, obj[0])
        worksheet.write(idx, 1, obj[1])
        worksheet.write(idx, 2, obj[2])
#    print '\n'
#    print 'Audio Set categories with their number of audio samples:\n'
#    for i in category_occurrences:
#        print str(i[0]).ljust(105) + str(i[1])


### SCRIPT ###
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

# --------------------------------------------------------------- #

# ------------------------ CREATE FILES --------------------------#

# DATASET FILE
sound_ids = sounds_with_labels.keys()
sound_ids.sort()
json.dump({node_id:list(result_final[node_id]) for node_id in result_final}, open('dataset.json', 'w'), indent=4)

# ALL IDS (FOR FRED)
json.dump(sound_ids, open('all_ids.json', 'w'))

# LICENSE FILE
# HOW TO - From console in kaggle/ (WARNING, DEMENDS A LOT OF MEMORY):
# >>> ipython
# >>> run main_v2.py
# >>> cd ..
# uncomment, copy the folowing script, and re-comment:

#import manager
#c = manager.Client(False)
#b = c.load_basket_pickle('freesound_db_160317.pkl')
#id_to_idx = {b.ids[idx]:idx for idx in range(len(b))}
#license_file = open('kaggle/licenses.txt', 'w')
#license_file.write("This dataset uses the following sounds from Freesound:\n\n")
#license_file.write("to access user page:  http://www.freesound.org/people/<username>\n")
#license_file.write("to access sound page: http://www.freesound.org/people/<username>/sounds/<soundid>\n\n")
#license_file.write("'<file name>' with ID <soundid> by <username> [<license>]\n\n")
#for sound_id in sound_ids:
#    sound = b.sounds[id_to_idx[sound_id]]
#    name = sound.name.encode('utf-8').replace('\r', '')
#    license_file.write("'{0}' of ID {1} by {2} [CC-{3}]\n"
#                       .format(name, sound.id, sound.username, sound.license.split('/')[-3].upper()))
#license_file.close()

# --------------------------------------------------------------- #

# ----------------------- SPLIT DEV EVAL -------------------------#

# STRUCTURE DATA, SPLIT SINGLE/MULTIPLE LABELED SOUNDS
sounds_single = {s:sounds_with_labels[s] for s in sounds_with_labels if len(sounds_with_labels[s])==1}
sounds_multiple = {s:sounds_with_labels[s] for s in sounds_with_labels if len(sounds_with_labels[s])>1}

data_single = {r:[] for r in result_final}
for s in sounds_single:
    data_single[sounds_single[s][0]].append(s)
    
data_multiple = {r:[] for r in result_final}
for s in sounds_multiple:
    for i in sounds_multiple[s]: 
        data_multiple[i].append(s)

# ORDER BY DURATION
# >>> cd ..
# uncomment, copy the folowing script, and re-comment:
#c = manager.Client(False)
#b = c.load_basket_pickle('freesound_db_160317.pkl')
#id_to_idx = {b.ids[idx]:idx for idx in range(len(b))}
#data_single_dur = {r:sorted([(s, b.sounds[id_to_idx[s]].duration) for s in data_single[r]], key=lambda c:c[1]) for r in data_single}
#data_multiple_dur = {r:sorted([(s, b.sounds[id_to_idx[s]].duration) for s in data_multiple[r]], key=lambda c:c[1]) for r in data_multiple}

# SPLIT DEV/EVAL FOR SINGLE LABELED WITH RATIO 3:2 BASED ON DURATION
#rule32 = ['dev', 'eval', 'dev', 'eval', 'dev']
#data_single_dev = {r:[] for r in data_single_dur}
#data_single_eval = {r:[] for r in data_single_dur}
#for r in data_single_dur:
#    for idx, s in enumerate(data_single_dur[r]):
#        if rule32[idx%5] == 'dev':
#            data_single_dev[r].append(s[0])
#        elif rule32[idx%5] == 'eval':
#            data_single_eval[r].append(s[0])
#
## RANDOMLY ADDING MULTIPLE LABELED WITH RATIO 3:2
#data_dev = data_single_dev
#data_eval = data_single_eval
#for idx, s in enumerate(sounds_multiple):
#    if rule32[idx%5] == 'dev':
#        for node_id in sounds_multiple[s]:
#            data_dev[node_id].append(s)
#    elif rule32[idx%5] == 'eval':
#        for node_id in sounds_multiple[s]:
#            data_eval[node_id].append(s)
#
## EXPORT DATASET
#ontology_by_id = {o['id']:o for o in data_onto}
#dataset_dev = [{'name': ontology_by_id[node_id]['name'], 
#                'audioset_id': node_id,
#                'sound_ids': data_dev[node_id],
#               } for node_id in data_dev]
#dataset_eval = [{'name': ontology_by_id[node_id]['name'], 
#                'audioset_id': node_id,
#                'sound_ids': data_eval[node_id],
#               } for node_id in data_eval]
#
#json.dump(dataset_dev, open('dataset_dev.json', 'w'), indent=4)
#json.dump(dataset_eval, open('dataset_eval.json', 'w'), indent=4)

# --------------------------------------------------------------- #

# ---------------------NOT NOW


# select only sounds with range 5-20 seconds **********************************

#
# # a deep copy will copy all contents by value
# data_duration_from5to20 = copy.deepcopy(data_duration)
#
# # data_duration_from5to20[0] no
#
#
# for key, value in data_duration.iteritems():
#     print key
#     # print value
#     print value['name']
#     print value['duration']
#     print value['aso_ids']
#     print('-------------------------')
#     if value['duration'] < MINLEN or value['duration'] > MAXLEN:
#         del data_duration_from5to20[key]
#

# outcome of constraint Hard1: rejecting durations less than 5 or greater than 20s
# from 268261 to 94700 sounds mapped from Freesound to the ASO, saved in variable data_duration_from5to20
# so there is 95k MAPPED sounds that meet this duration requirement (talking about clips here, not annotations)
