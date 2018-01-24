
import json
import numpy as np
import copy
# import xlsxwriter
# import matplotlib.pyplot as plt
import os
import sys
import time

FOLDER_DATA = 'kaggle3/'


#### DEFINE CONSTRAIN HERE ###
MINLEN = 0.3 # duration
MAXLEN = 30.0
MIN_VOTES_CAT = 30 # minimum number of votes per category to produce a QE.
# maybe useless cause all have more than 72 votes (paper)
MIN_HQ = 40 # minimum number of sounds with HQ labels per category
MIN_LQ = 80 # minimum number of sounds  with LQ labels per category
MIN_QE = 0.5 # minimum QE to accept the LQ as decent
MIN_HQ_LQ = 120 # minimum number of sounds between HQ and LQ labels per category

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


    # 1 U and NP
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
    data_sounds[catid]['QE'] = 0


# count cases where the mapping from votes to sounds fails
error_mapping_count_cats = []

""" # from data_votes to data_sounds ******************************************************************************"""

for catid, vote_groups in data_votes.iteritems():
    # list to keep track of assigned fsids within a category, to achieve disjoint subsets of audio samples
    fsids_assigned_cat = []
    error_mapping_count_cat = 0
    # print catid
    # print ()
    #
    #
    #

    # check GT in PP
    # check GT in the rest of the groups
    # if GT does not exist, take mapping decision without inter-annotator agreement
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


    # check GT in PNP
    # check GT in the remaining groups
    # if GT does not exist, take mapping decision without inter-annotator agreement
    for fsid in vote_groups['PNP']:
        # print fsid

        # only if the fsid has not been assigned in previous passes
        if fsid not in fsids_assigned_cat:
            # search for GT in this group
            if vote_groups['PNP'].count(fsid) > 1:
                if fsid not in fsids_assigned_cat:
                    data_sounds[catid]['PNP'].append(fsid)
                    fsids_assigned_cat.append(fsid)
            else:
                # search for GT in the remaining groups of votes
                data_sounds, fsids_assigned_cat, assigned = check_GT('U', fsid, catid, vote_groups, fsids_assigned_cat, data_sounds)
                if not assigned:
                    data_sounds, fsids_assigned_cat, assigned = check_GT('NP', fsid, catid, vote_groups, fsids_assigned_cat, data_sounds)

            # no GT was found for the annotation (2 votes in the same group).
            # we must take decisions without inter-annotator agreement

            if fsid not in fsids_assigned_cat:
                # map the voted sound to a disjoint group  without inter-annotator agreement
                data_sounds, fsids_assigned_cat, error_mapping_count_cat = map_votedsound_2_disjointgroups_wo_agreement(
                    fsid, catid, vote_groups, fsids_assigned_cat, data_sounds, error_mapping_count_cat)





    # check GT in U
    # check GT in the remaining groups
    # if GT does not exist, take mapping decision without inter-annotator agreement
    for fsid in vote_groups['U']:
        # print fsid

        # only if the fsid has not been assigned in previous passes
        if fsid not in fsids_assigned_cat:
            # search for GT in this group
            if vote_groups['U'].count(fsid) > 1:
                if fsid not in fsids_assigned_cat:
                    data_sounds[catid]['U'].append(fsid)
                    fsids_assigned_cat.append(fsid)
            else:
                # search for GT in the remaining groups of votes
                data_sounds, fsids_assigned_cat, assigned = check_GT('NP', fsid, catid, vote_groups, fsids_assigned_cat, data_sounds)

            # no GT was found for the annotation (2 votes in the same group).
            # we must take decisions without inter-annotator agreement

            if fsid not in fsids_assigned_cat:
                # map the voted sound to a disjoint group  without inter-annotator agreement
                data_sounds, fsids_assigned_cat, error_mapping_count_cat = map_votedsound_2_disjointgroups_wo_agreement(
                    fsid, catid, vote_groups, fsids_assigned_cat, data_sounds, error_mapping_count_cat)




    # check GT in NP
    # check GT in the remaining groups? no need to. already done in previous passes
    # if GT does not exist, take mapping decision without inter-annotator agreement
    for fsid in vote_groups['NP']:
        # print fsid

        # only if the fsid has not been assigned in previous passes
        if fsid not in fsids_assigned_cat:
            # search for GT in this group
            if vote_groups['NP'].count(fsid) > 1:
                if fsid not in fsids_assigned_cat:
                    data_sounds[catid]['NP'].append(fsid)
                    fsids_assigned_cat.append(fsid)
            # else: no need to. already done in previous passes
            #     # search for GT in the remaining groups of votes
            #     data_sounds, fsids_assigned_cat, assigned = check_GT('NP', fsid, catid, vote_groups, fsids_assigned_cat, data_sounds)

            # no GT was found for the annotation (2 votes in the same group).
            # we must take decisions without inter-annotator agreement
            else:
            # if fsid not in fsids_assigned_cat:
                # map the voted sound to a disjoint group  without inter-annotator agreement
                data_sounds, fsids_assigned_cat, error_mapping_count_cat = map_votedsound_2_disjointgroups_wo_agreement(
                    fsid, catid, vote_groups, fsids_assigned_cat, data_sounds, error_mapping_count_cat)

    # store mapping error for every category
    error_mapping_count_cats.append(error_mapping_count_cat)

    # for every category compute QE here number of votes len(PP) + len(PNP) / all
    # QE should only be computed if there are more than 20 votes? else not reliable
    if (len(vote_groups['PP']) + len(vote_groups['PNP']) + len(vote_groups['NP']) + len(vote_groups['U'])) >= MIN_VOTES_CAT:
        data_sounds[catid]['QE'] = (len(vote_groups['PP']) + len(vote_groups['PNP'])) / float(
            len(vote_groups['PP']) + len(vote_groups['PNP']) + len(vote_groups['NP']) + len(vote_groups['U']))
    # else:
    #     there is a category with 0 votes... because we have no sounds for it, hence no votes

    # sanity check: there should be no duplicated fsids within a group of data_sounds
    if (len(data_sounds[catid]['PP']) != len(set(data_sounds[catid]['PP'])) or
        len(data_sounds[catid]['PNP']) != len(set(data_sounds[catid]['PNP'])) or
        len(data_sounds[catid]['NP']) != len(set(data_sounds[catid]['NP'])) or
        len(data_sounds[catid]['U']) != len(set(data_sounds[catid]['U']))):
        # print('\n something unexpetected happened in the mapping********************* \n')
        print(catid)
        sys.exit('duplicates in data_sounds')

    # sanity check: groups in data_sounds should be disjoint
    if (list(set(data_sounds[catid]['PP']) & set(data_sounds[catid]['PNP'])) or
        list(set(data_sounds[catid]['PP']) & set(data_sounds[catid]['NP'])) or
        list(set(data_sounds[catid]['PP']) & set(data_sounds[catid]['U'])) or
        list(set(data_sounds[catid]['PNP']) & set(data_sounds[catid]['NP'])) or
        list(set(data_sounds[catid]['PNP']) & set(data_sounds[catid]['U'])) or
        list(set(data_sounds[catid]['NP']) & set(data_sounds[catid]['U']))):
        # print('\n something unexpetected happened in the mapping********************* \n')
        print(catid)
        sys.exit('data_sounds has not disjoint groups')

    # sanity check: number of sounds is equal in data_sounds (adding) and data_votes (concatenating groups and set)
    nb_sounds_data_sounds = (len(data_sounds[catid]['PP']) + len(data_sounds[catid]['PNP']) +\
                            len(data_sounds[catid]['NP']) + len(data_sounds[catid]['U']))
    all_votes = data_votes[catid]['PP'] + data_votes[catid]['PNP'] + data_votes[catid]['NP'] + data_votes[catid]['U']
    nb_sounds_data_votes = len(set(all_votes))
    if nb_sounds_data_sounds != nb_sounds_data_votes:
        # print('\n something unexpetected happened in the mapping********************* \n')
        print(catid)
        sys.exit('number of sounds is not equal in data_sounds and data_votes')






if sum(error_mapping_count_cats) > 0:
    print 'there are errors in the following number of fsids: ' + str(sum(error_mapping_count_cats))
    print(error_mapping_count_cats)

# TO DO
# check a few small categories in data_votes and data_sounds for testing



# here we have data_sounds ready to try.

""" # from data_sounds to data_qual_sets****************************************************************************"""
# let us create HQ and LQ with 2 versions. Then, apply filters step by step.

# create data_qual_sets with keys with catids and empty dicts as values
data_qual_sets = copy.deepcopy(data_votes)
for catid, groups in data_qual_sets.iteritems():
    data_qual_sets[catid].clear()



for ii in range(2):
    if ii == 0:
        # CASE A
        # HQ = PP
        # LQ = candidates - PP - NP. IT therefore includes: PNP + U + unvoted sounds
        # we use PNP as LQ, so HQ is even higher quality and avoid potential problems, eg incomplete labelling in EVAL
        # but this means we have less samples in HQ, which can reduce the number of categories
        print 'SCENARIO A: where HQ = PP and LQ = PNP + U + unvoted sounds'
        print()
        for catid, sound_groups in data_sounds.iteritems():
            data_qual_sets[catid]['HQ'] = sound_groups['PP']
            list_woPP = [item for item in sound_groups['candidates'] if item not in sound_groups['PP']]
            data_qual_sets[catid]['LQ'] = [item for item in list_woPP if item not in sound_groups['NP']]
            data_qual_sets[catid]['QE'] = sound_groups['QE']
    else:
        # CASE B
        # HQ = PP + PNP
        # LQ = candidates - PP - PNP - NP. IT therefore includes: U + unvoted sounds
        # we use PNP as HQ, so HQ has more heterogeneous content.
        # If there is a file with incomplete labelling in EVAL, it is not good
        # We can always leave them only for DEV
        # This means we have more samples in HQ, which can increment the number of categories
        # Maybe this is less clean but if needed...
        print 'SCENARIO B: where HQ = PP + PNP and LQ = U + unvoted sounds'
        print()
        for catid, sound_groups in data_sounds.iteritems():
            data_qual_sets[catid]['HQ'] = sound_groups['PP'] + sound_groups['PNP']
            list_woPP = [item for item in sound_groups['candidates'] if item not in sound_groups['PP']]
            list_woPP_PNP = [item for item in list_woPP if item not in sound_groups['PNP']]
            data_qual_sets[catid]['LQ'] = [item for item in list_woPP_PNP if item not in sound_groups['NP']]
            data_qual_sets[catid]['QE'] = sound_groups['QE']

    # sanity check: groups in data_qual_sets should be disjoint
    if list(set(data_qual_sets[catid]['HQ']) & set(data_qual_sets[catid]['LQ'])):
        # print('\n something unexpetected happened in the mapping********************* \n')
        print(catid)
        sys.exit('data_qual_sets has not disjoint groups')



    """ # apply strong filters to data_qual_sets***********************************************************************"""

    # Consider only leaf categories: 474 out of the initial 632
    # data_onto is a list of dictionaries
    # to retrieve them by id: for every dict o, we create another dict where key = o['id'] and value is o
    data_onto_by_id = {o['id']:o for o in data_onto}

    # for o in data_qual_sets. o = catid
    # create a dict of dicts. The latter are key=0, and value the actual value (data_qual_sets[o])
    data_qual_sets_l = {o: data_qual_sets[o] for o in data_qual_sets if len(data_onto_by_id[o]['child_ids'])<1}
    print 'Number of leaf categories: ' + str(len(data_qual_sets_l))
    print()

    # create copy of data_votes
    data_qual_sets_ld = copy.deepcopy(data_qual_sets_l)
    for catid, groups in data_qual_sets_ld.iteritems():
        data_qual_sets_ld[catid]['HQ'] = []
        data_qual_sets_ld[catid]['LQ'] = []

    # Apply duration filter: Of the 474 categories, keep sounds with durations [MINLEN: MAXLEN]
    for catid, groups in data_qual_sets_l.iteritems():
        for fsid in groups['HQ']:
            if data_duration[str(fsid)]['duration'] <= MAXLEN and data_duration[str(fsid)]['duration'] >= MINLEN:
                data_qual_sets_ld[catid]['HQ'].append(fsid)

        for fsid in groups['LQ']:
            if (data_duration[str(fsid)]['duration'] <= MAXLEN) and (data_duration[str(fsid)]['duration'] >= MINLEN):
                data_qual_sets_ld[catid]['LQ'].append(fsid)

    # the critical filter is the number of sounds with HQ. IT should not be less than MIN_HQ (what we proposed already)
    # o = catid. create a dict of dicts. the latter are just the dicts that fulfil the condition on MIN_HQ
    data_qual_sets_ld_HQ = {o: data_qual_sets_ld[o] for o in data_qual_sets_ld if len(data_qual_sets_ld[o]['HQ']) >= MIN_HQ}

    print 'Number of leaf categories with at least ' + str(MIN_HQ) + ' sounds with HQ labels, and of duration [' + str(MINLEN) + ':' +\
          str(MAXLEN) + ']: ' + str(len(data_qual_sets_ld_HQ))
    print()




    """ # apply flexible filters to data_qual_sets***********************************************************************"""

    print 'APPROACH ALFA'
    # number of sounds with LQ should not be less than MIN_LQ
    data_qual_sets_ld_HQLQ = {o: data_qual_sets_ld_HQ[o] for o in data_qual_sets_ld_HQ if len(data_qual_sets_ld_HQ[o]['LQ']) >= MIN_LQ}

    print 'Number of leaf categories with at least ' + str(MIN_HQ) + ' sounds with HQ labels, and at least ' + str(MIN_LQ) +\
          ' sounds with LQ labels, and of duration [' + str(MINLEN) + ':' + str(MAXLEN) + ']: ' + str(len(data_qual_sets_ld_HQLQ))

    # to trust the LQ subset, we demand a minimum QE
    data_qual_sets_ld_HQLQQE = {o: data_qual_sets_ld_HQLQ[o] for o in data_qual_sets_ld_HQLQ if data_qual_sets_ld_HQLQ[o]['QE'] >= MIN_QE}

    print 'Number of leaf categories with at least ' + str(MIN_HQ) + ' sounds with HQ labels, and at least ' + str(MIN_LQ) +\
          ' sounds with LQ labels with a QE > ' + str(MIN_QE) + ', and of duration ['\
          + str(MINLEN) + ':' + str(MAXLEN) + ']: ' + str(len(data_qual_sets_ld_HQLQQE))

    nb_dev_samples = []
    # esimate median of data samples
    for catid, groups in data_qual_sets_ld_HQLQQE.iteritems():
        nb_dev_samples.append(np.ceil(0.7*len(groups['HQ'])) + len(groups['LQ']))

    print 'Estimated Median of number of DEV samples per category: ' + str(np.median(nb_dev_samples))




    print()
    print()
    print 'APPROACH BETA'
    # CASE BETA
    # number of sounds amounted between HQ + LQ should not be less than MIN_HQ_LQ
    data_qual_sets_ld_HQLQb = {o: data_qual_sets_ld_HQ[o] for o in data_qual_sets_ld_HQ if
                              len(data_qual_sets_ld_HQ[o]['LQ']) + len(data_qual_sets_ld_HQ[o]['HQ']) >= MIN_HQ_LQ}

    print 'Number of leaf categories with at least ' + str(MIN_HQ) + ' sounds with HQ labels, and at least ' + str(MIN_HQ_LQ) +\
          ' sounds between HQ and LQ labels, and of duration [' + str(MINLEN) + ':' + str(MAXLEN) + ']: ' + str(len(data_qual_sets_ld_HQLQb))


    # to trust the LQ subset, we demand a minimum QE
    data_qual_sets_ld_HQLQQEb = {o: data_qual_sets_ld_HQLQb[o] for o in data_qual_sets_ld_HQLQb if data_qual_sets_ld_HQLQb[o]['QE'] >= MIN_QE}

    print 'Number of leaf categories with at least ' + str(MIN_HQ) + ' sounds with HQ labels, and at least ' + str(MIN_HQ_LQ) +\
          ' sounds between HQ and LQ labels with a QE > ' + str(MIN_QE) + ', and of duration ['\
          + str(MINLEN) + ':' + str(MAXLEN) + ']: ' + str(len(data_qual_sets_ld_HQLQQEb))

    nb_dev_samples = []
    # esimate median of data samples
    for catid, groups in data_qual_sets_ld_HQLQQEb.iteritems():
        nb_dev_samples.append(np.ceil(0.7*len(groups['HQ'])) + len(groups['LQ']))

    print 'Estimated Median of number of DEV samples per category: ' + str(np.median(nb_dev_samples))


    print '======================================================'
    print '\n\n\n'





a=9 #for debugging







# [len(data_qual_sets[l]['HQ']) for l in data_qual_sets.keys() if len(data_qual_sets[l]['HQ'])>40]