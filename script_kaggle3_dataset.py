
import json
import numpy as np
import copy
# import xlsxwriter
import matplotlib.pyplot as plt
import os
import sys
import time

FOLDER_DATA = 'kaggle3/'


#### DEFINE CONSTRAIN HERE ###
MINLEN = 0.0 # duration
MAXLEN = 30.0
MIN_INSTANCES = 40 # instance of sound per category





"""load initial data with votes, clip duration and ontology--------------------------------- """
'''------------------------------------------------------------------------------------------'''


# this the result of the mapping from FS sounds to ASO.
# 268k sounds with basic metadata and their corresponding ASO id.
# useful to get the duration of every sound
try:
    with open(FOLDER_DATA + 'json/FS_sounds_ASO_postIQA.json') as data_file:
        data_duration = json.load(data_file)
except:
    raise Exception('CHOOSE A MAPPING FILE AND ADD IT TO ' + FOLDER_DATA +'json/ FOLDER (THE FILE INCLUDE DURATION INFORMATION NEEDED)')



# load json with votes, to select only PP and PNP
# try:
#     with open(FOLDER_DATA + 'json/votes_sounds_annotations.json') as data_file:
#         data_votes = json.load(data_file)
# except:
#     raise Exception('ADD THE FILE CONTAINING THE VOTES (list of dict "value", "freesound_sound_id", "node_id") AND ADD IT TO THE FOLDER ' + FOLDER_DATA +'json/')

#
#
try:
# load json with ontology, to map aso_ids to understandable category names
    with open(FOLDER_DATA + 'json/ontology.json') as data_file:
         data_onto = json.load(data_file)
except:
    raise Exception('ADD AN ONTOLOGY JSON FILE TO THE FOLDER ' + FOLDER_DATA +'json/')



try:
# load json with ontology, to map aso_ids to understandable category names
    with open(FOLDER_DATA + 'json/votes_dumped_2018_Jan_22.json') as data_file:
         data_votes = json.load(data_file)
except:
    raise Exception('ADD AN ONTOLOGY JSON FILE TO THE FOLDER ' + FOLDER_DATA +'json/')


# data_votes is a dict where every key is a cat
# the value of every cat is a dict, that contains 5 keys: PP, PNP, NP, U, candidates
# the corresponding values are a list of Freesound ids





"""functions --------------------------------- """
'''------------------------------------------------------------------------------------------'''

def check_GT(group, fsid, catid, vote_groups, fsids_assigned_cat, data_sounds):
    # check if fsid has GT within a given group (PP,PNP,NP,U) of a category given by catid
    # if it does, add it to assigned fsids and send it to the corresponding group in data_sounds
    assigned = False
    if vote_groups[group].count(fsid) > 1:
        data_sounds[catid][group].append(fsid)
        fsids_assigned_cat.append(fsid)
        assigned = True
    return data_sounds, fsids_assigned_cat, assigned




def map_votedsound_2_disjointgroups_wo_agreement(fsid, catid, vote_groups, fsids_assigned_cat, data_sounds, error_mapping_count_cat):
    # map the voted sound to a disjoint group  without inter-annotator agreement
    # using set of arbitrary rules that cover all possible options
    # being demanding now. only sending to PP when we are sure

    # retrieve votes for fsid.
    # we know there is only one in PP
    votes = []
    if fsid in vote_groups['PP']:
        votes.append(1.0)
    if fsid in vote_groups['PNP']:
        votes.append(0.5)
    if fsid in vote_groups['U']:
        votes.append(0.0)
    if fsid in vote_groups['NP']:
        votes.append(-1.0)

    # votes has all the votes for fsid. let us take decisions

    # trivial cases where there is only one single vote by one annotator
    if 1.0 in votes and 0.5 not in votes and -1.0 not in votes and 0.0 not in votes:
        data_sounds[catid]['PP'].append(fsid)
        fsids_assigned_cat.append(fsid)
    elif 1.0 not in votes and 0.5 in votes and -1.0 not in votes and 0.0 not in votes:
        data_sounds[catid]['PNP'].append(fsid)
        fsids_assigned_cat.append(fsid)
    elif 1.0 not in votes and 0.5 not in votes and -1.0 in votes and 0.0 not in votes:
        data_sounds[catid]['NP'].append(fsid)
        fsids_assigned_cat.append(fsid)
    elif 1.0 not in votes and 0.5 not in votes and -1.0 not in votes and 0.0 in votes:
        data_sounds[catid]['U'].append(fsid)
        fsids_assigned_cat.append(fsid)


    # rest of 11 cases. placing first the PP options in case there is some error.

    # 8 PP and PNP
    elif 1.0 in votes and 0.5 in votes and -1.0 not in votes and 0.0 not in votes:
        data_sounds[catid]['PP'].append(fsid)
        fsids_assigned_cat.append(fsid)
    # 9 PP and PNP and U
    elif 1.0 in votes and 0.5 in votes and -1.0 not in votes and 0.0 in votes:
        data_sounds[catid]['PP'].append(fsid)
        fsids_assigned_cat.append(fsid)


    # 1
    elif 1.0 not in votes and 0.5 not in votes and -1.0 in votes and 0.0 in votes:
        data_sounds[catid]['NP'].append(fsid)
        fsids_assigned_cat.append(fsid)
    # 2
    elif 1.0 not in votes and 0.5 in votes and -1.0 not in votes and 0.0 in votes:
        data_sounds[catid]['U'].append(fsid)
        fsids_assigned_cat.append(fsid)
    # 3
    elif 1.0 not in votes and 0.5 in votes and -1.0 in votes and 0.0 not in votes:
        data_sounds[catid]['NP'].append(fsid)
        fsids_assigned_cat.append(fsid)
    # 4
    elif 1.0 not in votes and 0.5 in votes and -1.0 in votes and 0.0 in votes:
        data_sounds[catid]['NP'].append(fsid)
        fsids_assigned_cat.append(fsid)


    # 5
    elif 1.0 in votes and 0.5 not in votes and -1.0 not in votes and 0.0 in votes:
        data_sounds[catid]['U'].append(fsid)
        fsids_assigned_cat.append(fsid)
    # 6
    elif 1.0 in votes and 0.5 not in votes and -1.0 in votes and 0.0 not in votes:
        data_sounds[catid]['U'].append(fsid)
        fsids_assigned_cat.append(fsid)
    # 7
    elif 1.0 in votes and 0.5 not in votes and -1.0 in votes and 0.0 in votes:
        data_sounds[catid]['U'].append(fsid)
        fsids_assigned_cat.append(fsid)



    # 10
    elif 1.0 in votes and 0.5 in votes and -1.0 in votes and 0.0 not in votes:
        data_sounds[catid]['U'].append(fsid)
        fsids_assigned_cat.append(fsid)
    # 11
    elif 1.0 in votes and 0.5 in votes and -1.0 in votes and 0.0 in votes:
        data_sounds[catid]['U'].append(fsid)
        fsids_assigned_cat.append(fsid)

    else:
        # print('\n something unexpetected happened in the mapping********************* \n')
        error_mapping_count_cat += 1
        # sys.exit('something unexpetected happened in the mapping!')

    return data_sounds, fsids_assigned_cat, error_mapping_count_cat






# -------------------------end of fucntions-----------------------------------------------------------
# ----------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------





# sanity check:
# if there is duplicates in the candidates of a category


# create copy of data_votes
data_sounds = copy.deepcopy(data_votes)
for catid, vote_groups in data_sounds.iteritems():
    data_sounds[catid]['PP'] = []
    data_sounds[catid]['PNP'] = []
    data_sounds[catid]['NP'] = []
    data_sounds[catid]['U'] = []
    data_sounds[catid]['QA'] = 0


# count cases where the mapping from votes to sounds fails
error_mapping_count_cats = []



# from data_votes to data_sounds
for catid, vote_groups in data_votes.iteritems():
    # list to keep track of assigned fsids within a category, to achieve disjoint subsets of audio samples
    fsids_assigned_cat = []
    error_mapping_count_cat = 0
    # print catid
    # print ()

    for fsid in vote_groups['PP']:
        # print fsid
        # search for GT in this group
        if vote_groups['PP'].count(fsid) > 1:
            if fsid not in fsids_assigned_cat:
                data_sounds[catid]['PP'].append(fsid)
                fsids_assigned_cat.append(fsid)
        else:
            # search for GT in other groups of votes
            data_sounds, fsids_assigned_cat, assigned = check_GT('PNP', fsid, catid, vote_groups, fsids_assigned_cat, data_sounds)
            if not assigned:
                data_sounds, fsids_assigned_cat, assigned = check_GT('U', fsid, catid, vote_groups, fsids_assigned_cat, data_sounds)
            if not assigned:
                data_sounds, fsids_assigned_cat, assigned = check_GT('NP', fsid, catid, vote_groups, fsids_assigned_cat, data_sounds)


        # no GT was found for the annotation (2 votes in the same group).
        # we must take decisions without inter-annotator agreement

        if fsid not in fsids_assigned_cat:
            # map the voted sound to a disjoint group  without inter-annotator agreement
            data_sounds, fsids_assigned_cat, error_mapping_count_cat = map_votedsound_2_disjointgroups_wo_agreement(
                fsid, catid, vote_groups, fsids_assigned_cat, data_sounds, error_mapping_count_cat)
            error_mapping_count_cats.append(error_mapping_count_cat)




# replicate code por PNP U NP
# should be almost the same (minor changes...)
# chekc a few small categories for final result
# for every category compute QA here number of votes len(PP) + len(PNP) / all





a=9 #for debugging