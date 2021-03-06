
import json
import numpy as np
import copy

import matplotlib.pyplot as plt




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
# define constants
MINLEN = 5.0
# MAXLEN = 20.0
MAXLEN = 30.0
# MIN_INSTANCES = 50
MIN_INSTANCES = 40




# select only sounds that meet the following requirements:*********************************************************
# -their belonging to an ASO class has been manually validated as PP or PN?
# -they present duration ranging from 5-20 seconds.


data_votes_Present = list()

for idx, vote in enumerate(data_votes):
    # print value
    print vote['freesound_sound_id']
    print vote['node_id']
    print vote['value']
    print('-------------------------')

    #  preserve PP and PNP; reject Not Present and Unsure.
    if vote['value'] == 1.0 or vote['value'] == 0.5:
        data_votes_Present.append(vote)

# data_votes_Present is a list with all the annotations PP and PNP: 26683 in total
# this is a hard constraint.


print('---------------------------------------------------------------------------------------')
print ('now, how many of those are eligible according to duration?')
print('---------------------------------------------------------------------------------------')


data_votes_Present_from5to20 = list()

for idx, vote in enumerate(data_votes_Present):
    # print value
    print vote['freesound_sound_id']
    # check the duration of the sound with such and FS_id:
    # data_duration['228055']['duration'], in seconds
    print data_duration[str(vote['freesound_sound_id'])]['duration']
    print('-------------------------')

    #  preserve from 5 to 20s; else reject
    if data_duration[str(vote['freesound_sound_id'])]['duration'] >= MINLEN and\
                    data_duration[str(vote['freesound_sound_id'])]['duration'] <= MAXLEN:
        data_votes_Present_from5to20.append(vote)

# data_votes_Present_from5to20 is a list with all the annotations validated as PP and PNP,
# but only of sounds in the range 5-20s
# ONLY 8731 in total. This means 2/3 of the sounds are OUT this range!!!

# However, this number is irregularly distributed among a number of categories.
# it may be that one category has 70 and another 20 sounds.
# we need to know how populated every category is

dict_valid_cats = dict()


for idx, vote in enumerate(data_votes_Present_from5to20):
    print vote['node_id']
    print vote['freesound_sound_id']

    # if category already exists, as key in the dict
    # append the freesound_id to the existing list
    if str(vote['node_id']) in dict_valid_cats:
        dict_valid_cats[str(vote['node_id'])]['freesound_sound_id'].append(vote['freesound_sound_id'])
        dict_valid_cats[str(vote['node_id'])]['cat_size'] += 1

    else:
        # category is new in the dict
        # define new key with the aso_id (ie a category),
        # and the value is a dict, containing a list with all the sound_ids positive for such a category
        # define size = 1 to keep track of the size in this same variable
        # and include semantic name from ontology
        for i in np.arange(len(data_onto)):
            if vote['node_id'] == data_onto[i]['id']:
                cat_name = str(data_onto[i]['name'])
                break

        dict_valid_cats[str(vote['node_id'])] = {'cat_name': cat_name, 'freesound_sound_id': [vote['freesound_sound_id']], 'cat_size':1}
        # dict_valid_cats[str(vote['node_id'])] = {'freesound_sound_id': [vote['freesound_sound_id']]}

# dict_valid_cats is a dict with as many keys as sound categories with at least one sound that:
# -has presence of the sound category in it
# -has a duration ranging 5-20s
# the amount of categories is 473 categories

# BUT, how many categories have more than MIN_INSTANCES sounds?
# this will be the last hard constraint, after which we have to decide soft constraints.

count_valid_cats_MIN_INSTANCES=0
for key, value in dict_valid_cats.iteritems():
    if value['cat_size'] >= MIN_INSTANCES:
        print value['cat_name']
        print value['cat_size']
        print value['freesound_sound_id']
        count_valid_cats_MIN_INSTANCES += 1
        print ('--------------------------------------')

print ('---how many categories have more than MIN_INSTANCES sounds?\n')
print count_valid_cats_MIN_INSTANCES

# only 24 categories have more than 50 sounds, with the criteria defined above.


# sanity check:
count_all_sounds=0
cat_size_vector=list()
for key, value in dict_valid_cats.iteritems():
    count_all_sounds += value['cat_size']
    # to plot
    cat_size_vector.append(value['cat_size'])


if count_all_sounds != len(data_votes_Present_from5to20):
    print ('----things do not match')
else:
    print ('----calculus seems fine')


# plot
# y = [3, 10, 7, 5, 3, 4.5, 6, 8.1]
N = len(cat_size_vector)
x = range(N)
width = 1/1.5
plt.bar(x, cat_size_vector, width, color="blue")
plt.grid(True)
plt.xlabel('categories')
plt.ylabel('VALID sounds (after Presentness and duration filter')
plt.show()


plt.figure()
plt.bar(x, np.sort(cat_size_vector), width, color="blue")
plt.grid(True)
plt.xlabel('categories')
plt.ylabel('VALID sounds (after Presentness and duration filter)')
plt.show()



# TO DO:
# are there duplicates within the same category?
# or sounds that are voted more than once and therefore appear more than once in a given category?
# this would worsen the situation even more

# however, this number is not final, as a scarce child can populate the parent

# Comments: please check this is ok. the number is VERY LOW, but it seems correct to me...
# If this is the case:
# -we started with 26683 PRESENT annotations. this is the real starting point.
# -this number greatly reduced when the duration constraint is imposed (to 8731), ie 1/3 roughly
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

a=9





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




################# XF ######################
#
# PP and PNP for sounds duration <= 20 and durantion >= 5
result_5_20 = {o['id']:set() for o in data_onto}
for v in data_votes:
    if data_duration[str(v['freesound_sound_id'])]['duration']<=20 and data_duration[str(v['freesound_sound_id'])]['duration']>=5:
        if v['value']>0.4:
            result_5_20[v['node_id']].add(v['freesound_sound_id'])
print 'Number of categories with more than 50 sounds of duration [5;20]: ' + str(len([o for o in result if len(result_5_20[o])>=50]))

# PP and PNP for sounds duration <= 20
result_20 = {o['id']:set() for o in data_onto}
for v in data_votes:
    if data_duration[str(v['freesound_sound_id'])]['duration']<=20:
        if v['value']>0.4:
            result_20[v['node_id']].add(v['freesound_sound_id'])
print 'Number of categories with more than 50 sounds of duration <=20: ' + str(len([o for o in result if len(result_20[o])>50]))


# PP and PNP for sounds duration <= 30
result_30 = {o['id']:set() for o in data_onto}
for v in data_votes:
    if data_duration[str(v['freesound_sound_id'])]['duration']<=30:
        if v['value']>0.4:
            result_30[v['node_id']].add(v['freesound_sound_id'])
print 'Number of categories with more than 50 sounds of duration <=30: ' + str(len([o for o in result if len(result_30[o])>50]))
