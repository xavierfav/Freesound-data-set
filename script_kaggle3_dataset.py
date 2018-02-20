import json
import numpy as np
import copy
import matplotlib.pyplot as plt
import os
import sys
import time
import itertools
# import xlsxwriter


FOLDER_DATA = 'kaggle3/'

#### DEFINE CONSTRAIN HERE ###
MINLEN = 0.3  # duration
MAXLEN = 30.0
MIN_VOTES_CAT = 70  # minimum number of votes per category to produce a QE.
# maybe useless cause all have more than 72 votes (paper)

MIN_HQ = 40  # minimum number of sounds with HQ labels per category
# MIN_LQ = 75  # minimum number of sounds  with LQ labels per category
MIN_HQdev_LQ = 100  # minimum number of sounds between HQ and LQ labels per category
PERCENTAGE_DEV = 0.7 # split 70 / 30 for DEV / EVAL
# PERCENTAGE_DEV = 0.625 # split 62.5 / 27.5 for DEV / EVAL
MIN_QE = 0.7  # minimum QE to accept the LQ as decent
FLAG_BARPLOT = False
FLAG_BOXPLOT = False
FLAG_BARPLOT_PARENT = True
"""load initial data with votes, clip duration and ontology--------------------------------- """
'''------------------------------------------------------------------------------------------'''

# this the result of the mapping from FS sounds to ASO.
# 268k sounds with basic metadata and their corresponding ASO id.
# useful to get the duration of every sound
try:
    with open(FOLDER_DATA + 'json/FS_sounds_ASO_postIQA.json') as data_file:
        data_mapping = json.load(data_file)
except:
    raise Exception(
        'CHOOSE A MAPPING FILE AND ADD IT TO ' + FOLDER_DATA + 'json/ FOLDER (THE FILE INCLUDE DURATION INFORMATION NEEDED)')

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
    raise Exception('ADD AN ONTOLOGY JSON FILE TO THE FOLDER ' + FOLDER_DATA + 'json/')

# data_onto is a list of dictionaries
# to retrieve them by id: for every dict o, we create another dict where key = o['id'] and value is o
data_onto_by_id = {o['id']: o for o in data_onto}


try:
    # load json with ontology, to map aso_ids to understandable category names
    with open(FOLDER_DATA + 'json/votes_dumped_2018_Jan_22.json') as data_file:
        data_votes = json.load(data_file)
except:
    raise Exception('ADD AN ONTOLOGY JSON FILE TO THE FOLDER ' + FOLDER_DATA + 'json/')

# data_votes is a dict where every key is a cat
# the value of every cat is a dict, that contains 5 keys: PP, PNP, NP, U, candidates
# the corresponding values are a list of Freesound ids
#
#
#
#

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


def map_votedsound_2_disjointgroups_wo_agreement(fsid, catid, vote_groups, fsids_assigned_cat, data_sounds,
                                                 error_mapping_count_cat, count_risky_PP):
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
        # the only case where a sound is sent to PP without inter-annotator agreement
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
        data_sounds[catid]['PNP'].append(fsid)
        fsids_assigned_cat.append(fsid)
        count_risky_PP += 1
    # 9 PP and PNP and U
    elif 1.0 in votes and 0.5 in votes and -1.0 not in votes and 0.0 in votes:
        data_sounds[catid]['PNP'].append(fsid)
        fsids_assigned_cat.append(fsid)
        count_risky_PP += 1


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

    return data_sounds, fsids_assigned_cat, error_mapping_count_cat, count_risky_PP


# turn interactive mode on
plt.ion()


# SPLITFIGS = False
# SLAVE_BOXPLOT_DURATIONS = True



def plot_boxplot(data, x_labels, fig_title, y_label):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    # for tick in ax.get_xticklabels():
    #     tick.set_rotation(45)
    plt.xticks(fontsize=8, rotation=45)
    bp = ax.boxplot(data, patch_artist=True)
    ## change color and linewidth of the whiskers
    for whisker in bp['whiskers']:
        whisker.set(color='#7570b3', linewidth=1)

    for flier in bp['fliers']:
        flier.set(marker='.', color='#e7298a', alpha=0.5)

    ## change color and linewidth of the medians
    for median in bp['medians']:
        median.set(color='#ef0707', linewidth=3)

    ax.set_xticklabels(x_labels)
    plt.ylabel(y_label)
    plt.title(fig_title)
    plt.grid(True)
    plt.show()
    # plt.pause(0.001)


def plot_barplot(data_bottom, data_up, x_labels, y_label, fig_title, legenda):
    ind = np.arange(len(data_bottom))  # the x locations for the groups
    width = 0.5  # the width of the bars: can also be len(x) sequence
    # axes = [-0.5, len(data_bottom), 0, 170]

    fig = plt.figure()
    ax = fig.add_subplot(111)
    p1 = plt.bar(ind, data_bottom, width, color='b')
    p2 = plt.bar(ind, data_up, width, bottom=data_bottom, color='r')
    plt.xticks(fontsize=8, rotation=45)
    plt.xticks(ind, x_labels)
    plt.ylabel(y_label)
    plt.title(fig_title)
    # plt.yticks(np.arange(0, 81, 10))
    plt.legend((p1[0], p2[0]), legenda)
    # plt.axis(axes)
    ax.yaxis.grid(True)
    # plt.grid(True)
    plt.show()


def compute_median(data):
    nb_samples = []
    for id, group in data.iteritems():
        nb_samples.append(np.ceil(PERCENTAGE_DEV * len(group['HQ'])) + len(group['LQ']))
    # print 'Estimated Median of number of DEV samples per category: ' + str(np.median(nb_samples))
    # print()
    return nb_samples


def create_var_barplot(data_set, data_onto_by_id):
    # create variable with data for barplotting - function
    var_plot = []
    for catid, groups in data_set.iteritems():
        cat_plot = {}
        cat_plot['nbHQ_dev'] = np.ceil(PERCENTAGE_DEV * len(groups['HQ']))
        cat_plot['nbLQ'] = len(groups['LQ'])
        cat_plot['nbtotal_tr'] = cat_plot['nbHQ_dev'] + cat_plot['nbLQ']
        cat_plot['name'] = data_onto_by_id[str(catid)]['name']
        var_plot.append(cat_plot)
    return var_plot


# -------------------------end of functions-----------------------------------------------------------
# ----------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------


# create copy of data_votes
data_sounds = copy.deepcopy(data_votes)
for catid, vote_groups in data_sounds.iteritems():
    data_sounds[catid]['PP'] = []
    data_sounds[catid]['PNP'] = []
    data_sounds[catid]['NP'] = []
    data_sounds[catid]['U'] = []
    data_sounds[catid]['QE'] = 0    # initialzed to 0. only if more than MIN_VOTES_CAT, we compute it

# count cases where the mapping from votes to sounds fails
error_mapping_count_cats = []

""" # from data_votes to data_sounds ******************************************************************************"""
# to keep track of combinations
# PP + PNP and PP + PNP + U
count_risky_PP = 0

for catid, vote_groups in data_votes.iteritems():
    # list to keep track of assigned fsids within a category, to achieve disjoint subsets of audio samples
    fsids_assigned_cat = []
    error_mapping_count_cat = 0

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
            data_sounds, fsids_assigned_cat, assigned = check_GT('PNP', fsid, catid, vote_groups, fsids_assigned_cat,
                                                                 data_sounds)
            if not assigned:
                data_sounds, fsids_assigned_cat, assigned = check_GT('U', fsid, catid, vote_groups, fsids_assigned_cat,
                                                                     data_sounds)
            if not assigned:
                data_sounds, fsids_assigned_cat, assigned = check_GT('NP', fsid, catid, vote_groups, fsids_assigned_cat,
                                                                     data_sounds)

        # no GT was found for the annotation (2 votes in the same group).
        # we must take decisions without inter-annotator agreement

        if fsid not in fsids_assigned_cat:
            # map the voted sound to a disjoint group  without inter-annotator agreement
            data_sounds, fsids_assigned_cat, error_mapping_count_cat, count_risky_PP = map_votedsound_2_disjointgroups_wo_agreement(
                fsid, catid, vote_groups, fsids_assigned_cat, data_sounds, error_mapping_count_cat, count_risky_PP)

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
                data_sounds, fsids_assigned_cat, assigned = check_GT('U', fsid, catid, vote_groups, fsids_assigned_cat,
                                                                     data_sounds)
                if not assigned:
                    data_sounds, fsids_assigned_cat, assigned = check_GT('NP', fsid, catid, vote_groups,
                                                                         fsids_assigned_cat, data_sounds)

            # no GT was found for the annotation (2 votes in the same group).
            # we must take decisions without inter-annotator agreement

            if fsid not in fsids_assigned_cat:
                # map the voted sound to a disjoint group  without inter-annotator agreement
                data_sounds, fsids_assigned_cat, error_mapping_count_cat, count_risky_PP = map_votedsound_2_disjointgroups_wo_agreement(
                    fsid, catid, vote_groups, fsids_assigned_cat, data_sounds, error_mapping_count_cat, count_risky_PP)

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
                data_sounds, fsids_assigned_cat, assigned = check_GT('NP', fsid, catid, vote_groups, fsids_assigned_cat,
                                                                     data_sounds)

            # no GT was found for the annotation (2 votes in the same group).
            # we must take decisions without inter-annotator agreement

            if fsid not in fsids_assigned_cat:
                # map the voted sound to a disjoint group  without inter-annotator agreement
                data_sounds, fsids_assigned_cat, error_mapping_count_cat, count_risky_PP = map_votedsound_2_disjointgroups_wo_agreement(
                    fsid, catid, vote_groups, fsids_assigned_cat, data_sounds, error_mapping_count_cat, count_risky_PP)

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

            # no GT was found for the annotation (2 votes in the same group).
            # we must take decisions without inter-annotator agreement
            else:
                # if fsid not in fsids_assigned_cat:
                # map the voted sound to a disjoint group  without inter-annotator agreement
                data_sounds, fsids_assigned_cat, error_mapping_count_cat, count_risky_PP = map_votedsound_2_disjointgroups_wo_agreement(
                    fsid, catid, vote_groups, fsids_assigned_cat, data_sounds, error_mapping_count_cat, count_risky_PP)

    # store mapping error for every category
    error_mapping_count_cats.append(error_mapping_count_cat)

    # for every category compute QE here number of votes len(PP) + len(PNP) / all
    # QE should only be computed if there are more than MIN_VOTES_CAT votes. else not reliable
    if (len(vote_groups['PP']) + len(vote_groups['PNP']) + len(vote_groups['NP']) + len(
            vote_groups['U'])) >= MIN_VOTES_CAT:
        data_sounds[catid]['QE'] = (len(vote_groups['PP']) + len(vote_groups['PNP'])) / float(
            len(vote_groups['PP']) + len(vote_groups['PNP']) + len(vote_groups['NP']) + len(vote_groups['U']))

# =======================SANITY CHECKS===================================

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
    nb_sounds_data_sounds = (len(data_sounds[catid]['PP']) + len(data_sounds[catid]['PNP']) + \
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

print 'Number of sounds with voting combination (PP + PNP) or (PP + PNP + U) : ' + str(count_risky_PP)
# but this number is considering all the ontology, all durations, no filter has been applied yet.

# here we have data_sounds ready



""" # from data_sounds to data_qual_sets****************************************************************************"""
# let us create HQ and LQ with 2 versions. Then, apply filters step by step.

# create data_qual_sets with keys with catids and empty dicts as values
data_qual_sets = copy.deepcopy(data_votes)
for catid, groups in data_qual_sets.iteritems():
    data_qual_sets[catid].clear()

for ii in range(1):
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
            data_qual_sets[catid]['LQprior'] = sound_groups['PNP']
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

    nb_samples_cats_dev = compute_median(data_qual_sets)
    # plots before strong filters: all possible categories
    # if FLAG_PLOT:
    #     # boxplot number of examples per category in dev
    #     x_labels = 'estimated dev'
    #     fig_title = 'estimated number of clips in categories of DEV set'
    #     y_label = '# of audio clips'
    #     plot_boxplot(nb_samples_cats_dev, x_labels, fig_title, y_label)
    #
    #     # create variable with data for barplotting - function
    #     var_barplot = create_var_barplot(data_qual_sets, data_onto_by_id)
    #
    #     # barplot with number of sounds per category
    #     # sort by ascending number of TRAINING sounds in category (70% HQ + LQ)
    #     idx = np.argsort([var_barplot[tt]['nbtotal_tr'] for tt in range(len(var_barplot))])
    #     # idx = np.argsort([data_onto_rich[tt]['nbHQ_dev'] for tt in range(len(data_onto_rich))])
    #
    #     data_bottom = list(var_barplot[val]['nbLQ'] for val in idx)
    #     data_up = list(var_barplot[val]['nbHQ_dev'] for val in idx)
    #     x_labels = list(var_barplot[val]['name'] for val in idx)
    #     y_label = '# of audio clips'
    #     fig_title = 'number of DEV clips per category, split in HQdev and LQ, sorted by total'
    #     legenda = ('LQ', 'HQdev')
    #     plot_barplot(data_bottom, data_up, x_labels, y_label, fig_title, legenda)
    #


    # at this point we have: data_qual_sets, with dicts containing
    # HQ, LQ, QE for all categories (632)

    """ # apply STRONG filters to data_qual_sets********************************************************************"""

    # FILTER 1: Consider only leaf categories: 474 out of the initial 632
    # for o in data_qual_sets. o = catid
    # create a dict of dicts. The latter are key=o, and value the actual value (data_qual_sets[o])
    data_qual_sets_l = {o: data_qual_sets[o] for o in data_qual_sets if len(data_onto_by_id[o]['child_ids']) < 1}
    print 'Number of leaf categories: ' + str(len(data_qual_sets_l))
    # print()

    # plot
    nb_samples_cats_dev = compute_median(data_qual_sets_l)
    # plots before strong filters: all possible categories
    if FLAG_BOXPLOT:
        # boxplot number of examples per category in dev
        x_labels = 'estimated dev'
        fig_title = 'LEAVES: estimated number of clips in categories of DEV set'
        y_label = '# of audio clips'
        plot_boxplot(nb_samples_cats_dev, x_labels, fig_title, y_label)

    if FLAG_BARPLOT:
        # create variable with data for barplotting - function
        var_barplot = create_var_barplot(data_qual_sets_l, data_onto_by_id)

        # barplot with number of sounds per category
        # sort by ascending number of TRAINING sounds in category (70% HQ + LQ)
        idx = np.argsort([var_barplot[tt]['nbtotal_tr'] for tt in range(len(var_barplot))])
        # idx = np.argsort([data_onto_rich[tt]['nbHQ_dev'] for tt in range(len(data_onto_rich))])

        data_bottom = list(var_barplot[val]['nbLQ'] for val in idx)
        data_up = list(var_barplot[val]['nbHQ_dev'] for val in idx)
        x_labels = list(var_barplot[val]['name'] for val in idx)
        y_label = '# of audio clips'
        fig_title = 'LEAVES: number of DEV (' + str(PERCENTAGE_DEV*100) +  '%) clips per category, split in HQdev and LQ, sorted by total'
        legenda = ('LQ', 'HQdev')
        plot_barplot(data_bottom, data_up, x_labels, y_label, fig_title, legenda)



    # FILTER 2: Apply duration filter: Within the 474 categories, keep sounds with durations [MINLEN: MAXLEN]
    # create copy for result of filter
    data_qual_sets_ld = copy.deepcopy(data_qual_sets_l)
    for catid, groups in data_qual_sets_ld.iteritems():
        data_qual_sets_ld[catid]['HQ'] = []
        data_qual_sets_ld[catid]['LQ'] = []

    for catid, groups in data_qual_sets_l.iteritems():
        for fsid in groups['HQ']:
            if (data_mapping[str(fsid)]['duration'] <= MAXLEN) and (data_mapping[str(fsid)]['duration'] >= MINLEN):
                data_qual_sets_ld[catid]['HQ'].append(fsid)

        for fsid in groups['LQ']:
            if (data_mapping[str(fsid)]['duration'] <= MAXLEN) and (data_mapping[str(fsid)]['duration'] >= MINLEN):
                data_qual_sets_ld[catid]['LQ'].append(fsid)


    # FILTER 2.1: NC license. Within the categories, discard sounds with NC licenses
    # create copy for result of filter
    data_qual_sets_ldl = copy.deepcopy(data_qual_sets_ld)
    for catid, groups in data_qual_sets_ldl.iteritems():
        data_qual_sets_ldl[catid]['HQ'] = []
        data_qual_sets_ldl[catid]['LQ'] = []

    for catid, groups in data_qual_sets_ld.iteritems():
        for fsid in groups['HQ']:
            if data_mapping[str(fsid)]['license'].split('/')[-3] != 'by-nc':
                data_qual_sets_ldl[catid]['HQ'].append(fsid)

        for fsid in groups['LQ']:
            if data_mapping[str(fsid)]['license'].split('/')[-3] != 'by-nc':
                data_qual_sets_ldl[catid]['LQ'].append(fsid)


    # FILTER 3:  number of sounds with HQ>= MIN_HQ (what we proposed already)
    # o = catid. create a dict of dicts. the latter are just the dicts that fulfil the condition on MIN_HQ
    data_qual_sets_ld_HQ = {o: data_qual_sets_ldl[o] for o in data_qual_sets_ldl if
                            len(data_qual_sets_ldl[o]['HQ']) >= MIN_HQ}

    # data_qual_sets_ld_HQ means: every category with HQ and LQ after:
    # - taking leaves
    # - applying duration filter
    # - applying license filter (although not explicit in var name)

    print 'Number of leaf categories with at least ' + str(MIN_HQ) + ' sounds with HQ labels, and of duration [' + str(
        MINLEN) + ':' + \
          str(MAXLEN) + '], and NC-free: ' + str(len(data_qual_sets_ld_HQ))
    # print()

    # plot
    nb_samples_cats_dev = compute_median(data_qual_sets_ld_HQ)
    # plots before strong filters: all possible categories
    if FLAG_BOXPLOT:
        # boxplot number of examples per category in dev
        x_labels = 'estimated dev'
        fig_title = 'LEAVES | DUR | MIN_HQ: estimated number of clips in categories of DEV set'
        y_label = '# of audio clips'
        plot_boxplot(nb_samples_cats_dev, x_labels, fig_title, y_label)

    if FLAG_BARPLOT:
        # barplot with number of sounds per category
        # create variable with data for barplotting
        var_barplot = create_var_barplot(data_qual_sets_ld_HQ, data_onto_by_id)
        # sort by ascending number of TRAINING sounds in category (70% HQ + LQ)
        idx = np.argsort([var_barplot[tt]['nbtotal_tr'] for tt in range(len(var_barplot))])
        data_bottom = list(var_barplot[val]['nbLQ'] for val in idx)
        data_up = list(var_barplot[val]['nbHQ_dev'] for val in idx)
        x_labels = list(var_barplot[val]['name'] for val in idx)
        y_label = '# of audio clips'
        fig_title = 'LEAVES | DUR | MIN_HQ: number of DEV ('\
                    + str(PERCENTAGE_DEV*100) +  '%) clips per category, split in HQdev and LQ, sorted by total'
        legenda = ('LQ', 'HQdev')
        plot_barplot(data_bottom, data_up, x_labels, y_label, fig_title, legenda)

        # barplot again sorted by HQdev
        idx = np.argsort([var_barplot[tt]['nbHQ_dev'] for tt in range(len(var_barplot))])
        data_up = list(var_barplot[val]['nbLQ'] for val in idx)
        data_bottom = list(var_barplot[val]['nbHQ_dev'] for val in idx)
        x_labels = list(var_barplot[val]['name'] for val in idx)
        y_label = '# of audio clips'
        fig_title = 'LEAVES | DUR | MIN_HQ: number of DEV ('\
                    + str(PERCENTAGE_DEV*100) + '%) clips per category, split in HQdev and LQ, sorted by HQdev'
        legenda = ('HQdev', 'LQ')
        plot_barplot(data_bottom, data_up, x_labels, y_label, fig_title, legenda)



    """ # apply FLEXIBLE filters to data_qual_sets*****************************************************************"""

    # print 'APPROACH ALFA is more strict: separate threshold on HQ and LQ'
    # # FILTER 4: MIN_LQ. number of sounds with LQ should not be less than MIN_LQ
    # data_qual_sets_ld_HQLQ = {o: data_qual_sets_ld_HQ[o] for o in data_qual_sets_ld_HQ if
    #                           len(data_qual_sets_ld_HQ[o]['LQ']) >= MIN_LQ}
    # print 'Number of leaf categories with at least ' + str(MIN_HQ) + ' sounds with HQ labels, and at least ' + str(
    #     MIN_LQ) + ' sounds with LQ labels, and of duration [' + str(MINLEN) + ':' + str(MAXLEN) + ']: ' + str(
    #     len(data_qual_sets_ld_HQLQ))
    #
    #
    # # FILTER 5: MIN_QE. to trust the LQ subset, we demand a minimum QE
    # data_qual_sets_ld_HQLQQE = {o: data_qual_sets_ld_HQLQ[o] for o in data_qual_sets_ld_HQLQ if
    #                             data_qual_sets_ld_HQLQ[o]['QE'] >= MIN_QE}
    # print 'Number of leaf categories with at least ' + str(MIN_HQ) + ' sounds with HQ labels, and at least ' + str(
    #     MIN_LQ) + ' sounds with LQ labels with a QE > ' + str(MIN_QE) + ', and of duration [' \
    #       + str(MINLEN) + ':' + str(MAXLEN) + ']: ' + str(len(data_qual_sets_ld_HQLQQE))
    #
    #
    # # plot
    # nb_samples_cats_dev = compute_median(data_qual_sets_ld_HQLQQE)
    # # plots before strong filters: all possible categories
    # if FLAG_BOXPLOT:
    #     # boxplot number of examples per category in dev
    #     x_labels = 'estimated dev'
    #     fig_title = 'ALFA - LEAVES | DUR | MIN_HQ_LQ_QE: estimated number of clips in categories of DEV set'
    #     y_label = '# of audio clips'
    #     plot_boxplot(nb_samples_cats_dev, x_labels, fig_title, y_label)
    #
    # if FLAG_BARPLOT:
    #     # barplot with number of sounds per category
    #     # create variable with data for barplotting
    #     var_barplot = create_var_barplot(data_qual_sets_ld_HQLQQE, data_onto_by_id)
    #     # sort by ascending number of TRAINING sounds in category (70% HQ + LQ)
    #     idx = np.argsort([var_barplot[tt]['nbtotal_tr'] for tt in range(len(var_barplot))])
    #     data_bottom = list(var_barplot[val]['nbLQ'] for val in idx)
    #     data_up = list(var_barplot[val]['nbHQ_dev'] for val in idx)
    #     x_labels = list(var_barplot[val]['name'] for val in idx)
    #     y_label = '# of audio clips'
    #     fig_title = 'ALFA - LEAVES | DUR | MIN_HQ_LQ_QE: number of DEV ('\
    #                 + str(PERCENTAGE_DEV*100) +  '%) clips per category, split in HQdev and LQ, sorted by total'
    #     legenda = ('LQ', 'HQdev')
    #     plot_barplot(data_bottom, data_up, x_labels, y_label, fig_title, legenda)
    #
    # print 'Total Number of sounds in DEV set (estimated), there is a LOT of LQ: ' + str(sum(nb_samples_cats_dev))
    #
    #


    print()
    print()
    print 'APPROACH BETA is less strict: HQdev + LQ > MIN_HQdev_LQ (joint)'
    # CASE BETA
    # FILTER 4: MIN_HQdev_LQ. number of sounds amounted between HQdev + LQ s>= MIN_HQdev_LQ
    data_qual_sets_ld_HQLQb = {o: data_qual_sets_ld_HQ[o] for o in data_qual_sets_ld_HQ if
                               (len(data_qual_sets_ld_HQ[o]['LQ']) + np.ceil(PERCENTAGE_DEV *len(data_qual_sets_ld_HQ[o]['HQ']))) >= MIN_HQdev_LQ}

    # sanity
    for catid, groups in data_qual_sets_ld_HQLQb.iteritems():
        if (len(groups['LQ']) + np.ceil(PERCENTAGE_DEV *len(groups['HQ']))) < MIN_HQdev_LQ:
            print 'error in the category: ' + str(data_onto_by_id[str(catid)]['name'])

    print 'Number of leaf categories with at least ' + str(MIN_HQ) + ' sounds with HQ labels, and at least ' + str(
        MIN_HQdev_LQ) + ' sounds between HQdev and LQ labels, and of duration ['\
          + str(MINLEN) + ':' + str(MAXLEN) + '], and NC-free: ' + str(len(data_qual_sets_ld_HQLQb))




    # FILTER 5: MIN_QE. to trust the LQ subset, we demand a minimum QE

    # old way: hard constraint on QE
    # data_qual_sets_ld_HQLQQEb = {o: data_qual_sets_ld_HQLQb[o] for o in data_qual_sets_ld_HQLQb if
    #                              data_qual_sets_ld_HQLQb[o]['QE'] >= MIN_QE}
    #
    # print 'Number of leaf categories with at least ' + str(MIN_HQ) + ' sounds with HQ labels, and at least ' + str(
    #     MIN_HQdev_LQ) + ' sounds between HQdev and LQ labels with a QE > ' + str(MIN_QE) + ', and of duration [' \
    #       + str(MINLEN) + ':' + str(MAXLEN) + ']: ' + str(len(data_qual_sets_ld_HQLQQEb))
    #

    # new way: consider that some categories may not meet MIN_QE, but they may have enough HQ to fill MIN_HQdev_LQ
    data_qual_sets_ld_HQLQQEb = {}
    for o in data_qual_sets_ld_HQLQb:
        if data_qual_sets_ld_HQLQb[o]['QE'] >= MIN_QE:
            data_qual_sets_ld_HQLQQEb[o] = data_qual_sets_ld_HQLQb[o]

        # from here on, cannot trust LQ
        elif np.floor(PERCENTAGE_DEV * len(data_qual_sets_ld_HQLQb[o]['HQ'])) >= MIN_HQdev_LQ:
            # category with enough HQ to fill all DEV and EVAL without anything of LQ
            # keep HQ and empty LQ, and remove QE
            data_qual_sets_ld_HQLQQEb[o] = data_qual_sets_ld_HQLQb[o]
            data_qual_sets_ld_HQLQQEb[o]['LQ'] = []
            # could add LQprior here, but for now let us leave it. The category is already in anyway
            data_qual_sets_ld_HQLQQEb[o]['LQprior'] = []
            del data_qual_sets_ld_HQLQQEb[o]['QE']
            print '---category with enough HQ to fill DEV and EVAL withouth LQ: ' \
                  + str(data_onto_by_id[o]['name']) + ', with number of samples in HQ: ' \
                  + str(len(data_qual_sets_ld_HQLQb[o]['HQ']))
            print()

        # only happens for one category (orchestra). ignore for now
        # elif np.floor(PERCENTAGE_DEV * len(data_qual_sets_ld_HQLQb[o]['HQ'])) +\
        #         len(data_qual_sets_ld_HQLQb[o]['LQprior']) >= MIN_HQdev_LQ:
        #     # only HQ and LQprior together can fill all DEV
        #     # keep HQ, set LQ only to LQprior, keep LQprior and remove QE
        #     data_qual_sets_ld_HQLQQEb[o] = data_qual_sets_ld_HQLQb[o]
        #     data_qual_sets_ld_HQLQQEb[o]['LQ'] = data_qual_sets_ld_HQLQb[o]['LQprior']
        #     del data_qual_sets_ld_HQLQQEb[o]['QE']
        #     print '---category where only HQ and LQprior together can fill all DEV: ' \
        #           + str(data_onto_by_id[o]['name']) + ', with number of samples in HQ: ' \
        #           + str(len(data_qual_sets_ld_HQLQb[o]['HQ'])) + ', and number of samples in LQprior: ' \
        #           + str(len(data_qual_sets_ld_HQLQb[o]['LQprior']))
        #     print()


    print 'Number of leaf categories with at least ' + str(MIN_HQ) + ' sounds with HQ labels, and at least ' + str(
        MIN_HQdev_LQ) + ' sounds between HQdev and LQ labels with a QE > ' + str(MIN_QE) + ', and of duration [' \
          + str(MINLEN) + ':' + str(MAXLEN) + '], and NC-free: ' + str(len(data_qual_sets_ld_HQLQQEb))


    # plot
    nb_samples_cats_dev = compute_median(data_qual_sets_ld_HQLQQEb)
    # plots before strong filters: all possible categories
    if FLAG_BOXPLOT:
        # boxplot number of examples per category in dev
        x_labels = 'estimated dev'
        fig_title = 'BETA - LEAVES | DUR | MIN_HQdev_LQ: estimated number of clips in categories of DEV set'
        y_label = '# of audio clips'
        plot_boxplot(nb_samples_cats_dev, x_labels, fig_title, y_label)

    if FLAG_BARPLOT:
        # barplot with number of sounds per category
        # create variable with data for barplotting
        var_barplot = create_var_barplot(data_qual_sets_ld_HQLQQEb, data_onto_by_id)
        # sort by ascending number of TRAINING sounds in category (70% HQ + LQ)
        idx = np.argsort([var_barplot[tt]['nbtotal_tr'] for tt in range(len(var_barplot))])
        data_bottom = list(var_barplot[val]['nbLQ'] for val in idx)
        data_up = list(var_barplot[val]['nbHQ_dev'] for val in idx)
        x_labels = list(var_barplot[val]['name'] for val in idx)
        y_label = '# of audio clips'
        fig_title = 'BETA - LEAVES | DUR | MIN_HQdev_LQ_QE: number of DEV ('\
                    + str(PERCENTAGE_DEV*100) + '%) clips per category, split in HQdev and LQ, sorted by total'
        legenda = ('LQ', 'HQdev')
        plot_barplot(data_bottom, data_up, x_labels, y_label, fig_title, legenda)

        # barplot again sorted by HQdev
        idx = np.argsort([var_barplot[tt]['nbHQ_dev'] for tt in range(len(var_barplot))])
        data_up = list(var_barplot[val]['nbLQ'] for val in idx)
        data_bottom = list(var_barplot[val]['nbHQ_dev'] for val in idx)
        x_labels = list(var_barplot[val]['name'] for val in idx)
        y_label = '# of audio clips'
        fig_title = 'BETA - LEAVES | DUR | MIN_HQdev_LQ_QE: number of DEV ('\
                    + str(PERCENTAGE_DEV*100) + '%) clips per category, split in HQdev and LQ, sorted by HQdev'
        legenda = ('HQdev', 'LQ')
        plot_barplot(data_bottom, data_up, x_labels, y_label, fig_title, legenda)

    # review LQprior:make sure they are in LQ (some were deleted due to duration filter)
    for catid, groups in data_qual_sets_ld_HQLQQEb.iteritems():
        if len(list(set(groups['LQprior']) & set(groups['LQ']))) != len(groups['LQprior']):
            # print 'some LQ were gone in the child level, due to duration'
            data_qual_sets_ld_HQLQQEb[catid]['LQprior'] = list(set(groups['LQprior']) & set(groups['LQ']))



    print 'Total Number of sounds in DEV set (estimated), there is a LOT of LQ: ' + str(sum(nb_samples_cats_dev))
    print()
    print '======================================================'
    print '\n\n\n'



    """ # from data_qual_sets to data_qual_sets_pparents  *****************************************************
    ***********************************************************************************************************
    ***********************************************************************************************************"""


    # So far we have considered only leafs. Now, there are parents such that all the childrens are discarded.
    # we could try to aggregate these children together (the part of them that it is ok)
    # with the parent (if applicable), and see if the resulting aggregated category meets the requirements.
    # how many categories are gained?

    # final set of valid leaf categories for dataset
    final_set_valid_leafs = [catid for catid in data_qual_sets_ld_HQLQQEb]

    # list all penultimate parents (parents at the penultimate level of the onto)
    penul_parents = []
    for catid, info in data_onto_by_id.iteritems():
        # if they have children
        if info['child_ids']:
            # but none of the children have further children
            flag_penul_parent = True
            for childid in info['child_ids']:
                if data_onto_by_id[str(childid)]['child_ids']:
                    flag_penul_parent = False
                    break
            if flag_penul_parent:
                penul_parents.append({'catid': catid, 'name': data_onto_by_id[str(catid)]['name']})
                # print (data_onto_by_id[str(catid)]['name'])

    print 'There are ' + str(len(penul_parents)) + ' penultimate parents\n'

    # how many of the penultimate parents have ALL children discarded for the dataset (due to ANY reason)?
    penul_parents_cand = []
    for penul_parent in penul_parents:
        flag_all_children_discarded = True
        for childid in data_onto_by_id[penul_parent['catid']]['child_ids']:
            if childid in final_set_valid_leafs:
                flag_all_children_discarded = False
                break
        if flag_all_children_discarded:
            penul_parents_cand.append({'catid': penul_parent['catid'], 'name': penul_parent['name']})
            # print (penul_parent['name'])

    print 'There are ' + str(len(penul_parents_cand)) + ' penultimate parents; ALL children either ' \
                                                        'not eligible (eg RED) or discarded for the dataset\n'

    # these penultimate parents with ALL children not eligible or discarded, are candidates to be part of the dataset
    # they are candidates to be "new children"

    # we have to populate them with their useless children (join them):
    # 1- only consider the children that do not have multiple parents.
    # For example, HISS is a child and has multiple parents (cat, steam, snake, onomatopeia)
    # u cannot say that a steam hiss is a cat hiss, so we cannot propagate from hiss to cat.
    # but the rest of the Cat's children can be populated (meouw, purr, etc)

    # 2-populate parents with valid children: HQ, LQ
    # concatenate lists of HQ and LQ (easy)? set
    # but the concepts of LQ and HQ are different when we populate higher in the hierarchy.
    # it can happen that in child it is LQ while it is HQ in parent: for example, if we have a meow and a purr,
    # it will be PNP on any of the children, but PP on the immediate parent CAT
    # we do not know this. it could also be that there is purr + speech (category outside the 'family'), and so
    # it must stay PNP both in children and parent.
    # The easiest thing, and more restrictive/demanding/ensuring better quality is:
    # join HQ and join LQ. whatever it is HQ in children, it should also be in parent.
    # and in this way, the LQ will be of better quality
    # but there are several cases to be consider. doing it exhaustively.

    # 3-recompute the QE, with votes... think cases: sound in children OR in father vs sound in both
    # could be contradictory votes. A cat purr candidate to meow




    # create data_qual_sets_pparents with keys with catids and empty dicts as values, filled with empty lists for HQ/LQ
    data_qual_sets_pparents = copy.deepcopy(data_qual_sets)
    for catid, groups in data_qual_sets_pparents.iteritems():
        data_qual_sets_pparents[catid].clear()
        data_qual_sets_pparents[catid]['HQ'] = []
        data_qual_sets_pparents[catid]['LQ'] = []

    penul_parents_cand_2filt = []
    counter_mult_parents = 0

    for penul_parent in penul_parents_cand:

        """ # 1) distribute children  *****************************************************
        ***********************************************************************************************************"""

        if penul_parent['name'] == 'Telephone':
            a = 9

        count_weird_pop_fromHQ2LQ = 0
        children_valid_popul_HQLQ = []
        children_valid_popul_onlyHQ = []
        for childid in data_onto_by_id[penul_parent['catid']]['child_ids']:

            # 1- for every child: if there is no multiple parents
            nb_parents = len([parentid for parentid in data_onto_by_id if childid in data_onto_by_id[str(parentid)]['child_ids']])

            if nb_parents == 1:
                # only consider children withOUT multiple parents

                # checking minimum QE for every category individually, for simplicity
                if data_qual_sets[str(childid)]['QE'] > MIN_QE:
                    # the number of votes > MIN_VOTES_CAT was checked before. it not, QE = 0 already
                    children_valid_popul_HQLQ.append(childid)
                elif data_qual_sets[str(childid)]['HQ']:
                    children_valid_popul_onlyHQ.append(childid)

            elif nb_parents == 0:
                sys.exit('mistake at multiple parents computation')
            else:
                counter_mult_parents += 1

        # here we have children_valid_popul_HQLQ with the valid children for penul_parent, including ['QE'] > MIN_QE:
        # and children_valid_popul_onlyHQ with the valid children for penul_parent that do not meet QE


        # 2 - when populating there are several cases possible
        # a) sound appears twice in HQ, or on LQ. Do set to keep it once. sanity check.

        # b,c,d are only the most typical of a series of combinations that may happen. covered below in basic if-clauses

        # b) sound appears in parent_HQ and child_LQ:
        # if we have a meow and a purr (PNP) or if you are Unsure between a purr/meow
        # count how many times this happens. leave in parent_HQ

        # c) sound appears in parent_LQ and child_HQ: is this possible? in theory it should not:
        # - absence of noise in one means it is also absent in the other
        # - PP in children, means PP in parent.
        # monitor this. it could happen due to different subjective evaluation.
        # same file rated differently by different people.
        # count how many times this happens. leave in parent_LQ.

        # d) once you merge the children, it can happen that a sound is in HQ and LQ
        # sound with a meow and a purr (with both tags) can be candidate in both siblings
        # it can be validated as PP by userA (wrong doing), goes to HQ, but
        # but as PNP by userB in purr, goes to LQ
        # goes to parent_HQ

        # extend lists of HQ/LQ sounds of all children to populate
        children_id_2_parent_HQ = []
        children_id_2_parent_LQ = []
        if children_valid_popul_onlyHQ and not children_valid_popul_HQLQ:
            # only populating HQ
            children_id_2_parent_HQ.extend(children_valid_popul_onlyHQ)

        elif not children_valid_popul_onlyHQ and children_valid_popul_HQLQ:
            # only populating both HQ and LQ
            children_id_2_parent_HQ.extend(children_valid_popul_HQLQ)
            children_id_2_parent_LQ.extend(children_valid_popul_HQLQ)

        elif children_valid_popul_onlyHQ and children_valid_popul_HQLQ:
            # populating both ways: (HQ and LQ) and only HQ
            children_id_2_parent_HQ.extend(children_valid_popul_onlyHQ)
            children_id_2_parent_HQ.extend(children_valid_popul_HQLQ)
            children_id_2_parent_LQ.extend(children_valid_popul_HQLQ)
        # else:
            # print 'no children to populate'

        if children_id_2_parent_HQ:
            # at least we have to populate HQ
            # consider HQ and LQ
            # grab all valid children, merge into list, set
            children_joint_lists_HQ = [data_qual_sets[str(childid)]['HQ'] for childid in children_id_2_parent_HQ]
            children_joint_HQ = list(set(list(itertools.chain.from_iterable(children_joint_lists_HQ))))
            # the latter should not produce duplicates

            # distribution of children------------------------------------make function
            for id in children_joint_HQ:
                # sound only in children. several options
                if id not in data_qual_sets[penul_parent['catid']]['HQ'] and id not in data_qual_sets[penul_parent['catid']]['LQ']:
                    data_qual_sets_pparents[penul_parent['catid']]['HQ'].append(id)

                    # sound also in parent_HQ
                elif id in data_qual_sets[penul_parent['catid']]['HQ']:
                    data_qual_sets_pparents[penul_parent['catid']]['HQ'].append(id)

                    # sound also in parent_LQ
                elif id in data_qual_sets[penul_parent['catid']]['LQ']:
                    data_qual_sets_pparents[penul_parent['catid']]['LQ'].append(id)
                    count_weird_pop_fromHQ2LQ += 1


        if children_id_2_parent_LQ:
            # we also have to populate LQ (this only happens if there is children_joint_HQ too)
            children_joint_lists_LQ = [data_qual_sets[str(childid)]['LQ'] for childid in children_id_2_parent_LQ]
            children_joint_LQ = list(set(list(itertools.chain.from_iterable(children_joint_lists_LQ))))
            # the latter could produce duplicates

            for id in children_joint_LQ:
                # sound only in children. several options
                if id not in data_qual_sets[penul_parent['catid']]['HQ'] and id not in \
                        data_qual_sets[penul_parent['catid']]['LQ']:
                    if id in children_joint_LQ and id not in children_joint_HQ:
                        data_qual_sets_pparents[penul_parent['catid']]['LQ'].append(id)
                    elif id in children_joint_LQ and id in children_joint_HQ:
                        data_qual_sets_pparents[penul_parent['catid']]['HQ'].append(id)

                    # sound also in parent_HQ
                elif id in data_qual_sets[penul_parent['catid']]['HQ']:
                    data_qual_sets_pparents[penul_parent['catid']]['HQ'].append(id)

                    # sound also in parent_LQ
                elif id in data_qual_sets[penul_parent['catid']]['LQ']:
                    data_qual_sets_pparents[penul_parent['catid']]['LQ'].append(id)


        # so far: the children have been distributed in a disjoint fashion


        """ # 2) distribute parent  *****************************************************
        ***********************************************************************************************************"""

        # now, independent of the children, add the parents if QE allows it
        # these categories were not considered before because they were not leafs
        FLAG_PARENT_IN = 0
        if data_qual_sets[penul_parent['catid']]['QE'] >= MIN_QE:
            # add both HQ and LQ
            FLAG_PARENT_IN = 2
            data_qual_sets_pparents[penul_parent['catid']]['HQ'].extend(data_qual_sets[penul_parent['catid']]['HQ'])
            data_qual_sets_pparents[penul_parent['catid']]['LQ'].extend(data_qual_sets[penul_parent['catid']]['LQ'])

        else:
            # we cannot trust LQ. Add only HQ
            FLAG_PARENT_IN = 1
            data_qual_sets_pparents[penul_parent['catid']]['HQ'].extend(data_qual_sets[penul_parent['catid']]['HQ'])


        # remove duplicates from the process
        data_qual_sets_pparents[penul_parent['catid']]['HQ'] = \
            list(set(data_qual_sets_pparents[penul_parent['catid']]['HQ']))
        data_qual_sets_pparents[penul_parent['catid']]['LQ'] = \
            list(set(data_qual_sets_pparents[penul_parent['catid']]['LQ']))


        """ # 3) sanity checks  *****************************************************
        ***********************************************************************************************************"""

        # sanity check: number of sounds must be equal before and after population

        # sounds after the processing
        nb_sounds_postpop = len(data_qual_sets_pparents[penul_parent['catid']]['HQ']) + \
                            len(data_qual_sets_pparents[penul_parent['catid']]['LQ'])

        if children_valid_popul_HQLQ:
            # both types of population
            # sometimes you get dual population from the children (HQ and LQ at the same time)
            # sometimes you get only HQ population from the children (not enough QE)

            # concatenating lists and set
            if FLAG_PARENT_IN == 2:
                nb_sounds_prepop = len(set(children_joint_HQ + children_joint_LQ +
                                           data_qual_sets[penul_parent['catid']]['HQ'] +
                                           data_qual_sets[penul_parent['catid']]['LQ']))
            elif FLAG_PARENT_IN == 1:
                nb_sounds_prepop = len(set(children_joint_HQ + children_joint_LQ +
                                           data_qual_sets[penul_parent['catid']]['HQ']))
            elif FLAG_PARENT_IN == 0:
                nb_sounds_prepop = len(set(children_joint_HQ + children_joint_LQ))
            else:
                sys.exit('sanity check number of sounds')

            if nb_sounds_prepop != nb_sounds_postpop:
                print(penul_parent)
                sys.exit('number of sounds is not equal before and after population'
                         ' - both populations together (HQ and/or dual population (always HQ and LQ))')

        elif children_valid_popul_onlyHQ:
            # only HQ population from the children (not enough QE)

            # concatenating lists and set
            if FLAG_PARENT_IN == 2:
                nb_sounds_prepop = len(set(children_joint_HQ +
                                           data_qual_sets[penul_parent['catid']]['HQ'] +
                                           data_qual_sets[penul_parent['catid']]['LQ']))
            elif FLAG_PARENT_IN == 1:
                nb_sounds_prepop = len(set(children_joint_HQ +
                                           data_qual_sets[penul_parent['catid']]['HQ']))
            elif FLAG_PARENT_IN == 0:
                nb_sounds_prepop = len(set(children_joint_HQ))
            else:
                sys.exit('sanity check number of sounds')

            if nb_sounds_prepop != nb_sounds_postpop:
                print(catid)
                sys.exit('number of sounds is not equal before and after population - only HQ population')

        else:
            # no population from the children
            # concatenating lists and set
            if FLAG_PARENT_IN == 2:
                nb_sounds_prepop = len(set(data_qual_sets[penul_parent['catid']]['HQ'] +
                                           data_qual_sets[penul_parent['catid']]['LQ']))
            elif FLAG_PARENT_IN == 1:
                nb_sounds_prepop = len(set(data_qual_sets[penul_parent['catid']]['HQ']))
            elif FLAG_PARENT_IN == 0:
                nb_sounds_prepop = 0
            else:
                sys.exit('sanity check number of sounds')

            if nb_sounds_prepop != nb_sounds_postpop:
                print(penul_parent)
                sys.exit('number of sounds is not equal before and after population - no population from children')


        # how many penultimate parents (populated or not) are we considering?)
        # sometimes we populate them, having parent + child(ren)
        # or we dont consider the children but we consider the parent (for the first time)
        # or we dont consider the parent (due to QE) but the aggregation of the children
        if data_qual_sets_pparents[penul_parent['catid']]['HQ']:
            # if we actually have a new candidate category, sanity check

            # HQ and LQ must be disjoint groups
            if list(set(data_qual_sets_pparents[penul_parent['catid']]['HQ']) &
                    set(data_qual_sets_pparents[penul_parent['catid']]['LQ'])):
                print(penul_parent)
                sys.exit('data_qual_sets_pparents has not disjoint groups. beware population')

            penul_parents_cand_2filt.append(penul_parent)

    print 'There are ' + str(len(penul_parents_cand_2filt)) + ' penultimate parents entering the filtering stage, ie ' \
                                                              'after MultParents, indiv QE filter and population\n'


# remove empty categories from data_qual_sets_pparents (keep only the penultimate parents)
data_qual_sets_pparents_clean = {o: data_qual_sets_pparents[o] for o in data_qual_sets_pparents if data_qual_sets_pparents[o]['HQ']}
print 'Number of added penultimate parents entering the filtering stage: ' + str(len(data_qual_sets_pparents_clean))

# sanity check: dict of valid children and parents are disjoint at this point
if any(k in data_qual_sets_ld_HQLQQEb for k in data_qual_sets_pparents_clean):
    sys.exit('dicts of parent and children are not disjoint. DANGER')



""" # 4) once we have the new children, repeat filtering as if they were real children. ***********************
***********************************************************************************************************"""

# FILTER 2: Apply duration filter: Within the categories, keep sounds with durations [MINLEN: MAXLEN]
# create copy for next filter
data_qual_sets_pparents_d = copy.deepcopy(data_qual_sets_pparents_clean)
for catid, groups in data_qual_sets_pparents_d.iteritems():
    data_qual_sets_pparents_d[catid]['HQ'] = []
    data_qual_sets_pparents_d[catid]['LQ'] = []

for catid, groups in data_qual_sets_pparents_clean.iteritems():
    for fsid in groups['HQ']:
        if (data_mapping[str(fsid)]['duration'] <= MAXLEN and data_mapping[str(fsid)]['duration'] >= MINLEN):
            data_qual_sets_pparents_d[catid]['HQ'].append(fsid)

    for fsid in groups['LQ']:
        if (data_mapping[str(fsid)]['duration'] <= MAXLEN) and (data_mapping[str(fsid)]['duration'] >= MINLEN):
            data_qual_sets_pparents_d[catid]['LQ'].append(fsid)



# FILTER 3: number of sounds with HQ>= MIN_HQ
# o = catid. create a dict of dicts. the latter are just the dicts that fulfil the condition on MIN_HQ
data_qual_sets_pparents_d_HQ = {o: data_qual_sets_pparents_d[o] for o in data_qual_sets_pparents_d if
                        len(data_qual_sets_pparents_d[o]['HQ']) >= MIN_HQ}

print 'Number of pop parent categories with at least ' + str(MIN_HQ) + ' sounds with HQ labels, and of duration [' + \
      str(MINLEN) + ':' + str(MAXLEN) + ']: ' + str(len(data_qual_sets_pparents_d_HQ))
# print()


print()
print()
print 'APPROACH BETA is less strict: HQdev + LQ > MIN_HQdev_LQ (joint)'
# CASE BETA
# FILTER 4: MIN_HQdev_LQ. number of sounds amounted between HQdev + LQ s>= MIN_HQdev_LQ
data_qual_sets_pparents_d_HQLQb = {o: data_qual_sets_pparents_d_HQ[o] for o in data_qual_sets_pparents_d_HQ if
                           (len(data_qual_sets_pparents_d_HQ[o]['LQ']) + np.ceil(
                               PERCENTAGE_DEV * len(data_qual_sets_pparents_d_HQ[o]['HQ']))) >= MIN_HQdev_LQ}

# sanity
for catid, groups in data_qual_sets_pparents_d_HQLQb.iteritems():
    if (len(groups['LQ']) + np.ceil(PERCENTAGE_DEV * len(groups['HQ']))) <= MIN_HQdev_LQ:
        print 'error in the category: ' + str(data_onto_by_id[str(catid)]['name'])

print 'Number of pop parent categories with at least ' + str(MIN_HQ) + ' sounds with HQ labels, and at least ' + str(
    MIN_HQdev_LQ) + ' sounds between HQdev and LQ labels, and of duration [' \
      + str(MINLEN) + ':' + str(MAXLEN) + ']: ' + str(len(data_qual_sets_pparents_d_HQLQb))

if FLAG_BARPLOT_PARENT:
    # barplot with number of sounds per category
    # create variable with data for barplotting
    var_barplot = create_var_barplot(data_qual_sets_pparents_d_HQLQb, data_onto_by_id)
    # sort by ascending number of TRAINING sounds in category (70% HQ + LQ)
    idx = np.argsort([var_barplot[tt]['nbtotal_tr'] for tt in range(len(var_barplot))])
    data_bottom = list(var_barplot[val]['nbLQ'] for val in idx)
    data_up = list(var_barplot[val]['nbHQ_dev'] for val in idx)
    x_labels = list(var_barplot[val]['name'] for val in idx)
    y_label = '# of audio clips'
    fig_title = 'BETA - PPARENTS | DUR | MIN_HQdev_LQ: number of DEV (' \
                + str(PERCENTAGE_DEV * 100) + '%) clips per category, split in HQdev and LQ, sorted by total'
    legenda = ('LQ', 'HQdev')
    plot_barplot(data_bottom, data_up, x_labels, y_label, fig_title, legenda)

    # barplot again sorted by HQdev
    idx = np.argsort([var_barplot[tt]['nbHQ_dev'] for tt in range(len(var_barplot))])
    data_up = list(var_barplot[val]['nbLQ'] for val in idx)
    data_bottom = list(var_barplot[val]['nbHQ_dev'] for val in idx)
    x_labels = list(var_barplot[val]['name'] for val in idx)
    y_label = '# of audio clips'
    fig_title = 'BETA - PPARENTS | DUR | MIN_HQdev_LQ: number of DEV (' \
                + str(PERCENTAGE_DEV * 100) + '%) clips per category, split in HQdev and LQ, sorted by HQdev'
    legenda = ('HQdev', 'LQ')
    plot_barplot(data_bottom, data_up, x_labels, y_label, fig_title, legenda)




""" 5) Merge both dictionaries and save********************************************************************************
****************************************************************************************************************"""


# joint both dicts
dataset_final = dict(data_qual_sets_ld_HQLQQEb)  # or orig.copy()
dataset_final.update(data_qual_sets_pparents_d_HQLQb)
print 'Number of final categories: ' + str(len(dataset_final))

if FLAG_BARPLOT_PARENT:
    # barplot with number of sounds per category
    # create variable with data for barplotting
    var_barplot = create_var_barplot(dataset_final, data_onto_by_id)
    # sort by ascending number of TRAINING sounds in category (70% HQ + LQ)
    idx = np.argsort([var_barplot[tt]['nbtotal_tr'] for tt in range(len(var_barplot))])
    data_bottom = list(var_barplot[val]['nbLQ'] for val in idx)
    data_up = list(var_barplot[val]['nbHQ_dev'] for val in idx)
    x_labels = list(var_barplot[val]['name'] for val in idx)
    y_label = '# of audio clips'
    fig_title = 'BETA - PPARENTS | DUR | MIN_HQdev_LQ: number of DEV (' \
                + str(PERCENTAGE_DEV * 100) + '%) clips per category, split in HQdev and LQ, sorted by total'
    legenda = ('LQ', 'HQdev')
    plot_barplot(data_bottom, data_up, x_labels, y_label, fig_title, legenda)

    # barplot again sorted by HQdev
    idx = np.argsort([var_barplot[tt]['nbHQ_dev'] for tt in range(len(var_barplot))])
    data_up = list(var_barplot[val]['nbLQ'] for val in idx)
    data_bottom = list(var_barplot[val]['nbHQ_dev'] for val in idx)
    x_labels = list(var_barplot[val]['name'] for val in idx)
    y_label = '# of audio clips'
    fig_title = 'BETA - PPARENTS | DUR | MIN_HQdev_LQ: number of DEV (' \
                + str(PERCENTAGE_DEV * 100) + '%) clips per category, split in HQdev and LQ, sorted by HQdev'
    legenda = ('HQdev', 'LQ')
    plot_barplot(data_bottom, data_up, x_labels, y_label, fig_title, legenda)

# save
with open('dataset_final.json', 'w') as fp:
    json.dump(dataset_final, fp)



"""**********************************END OF INITIAL STAGE: *****************************************************
****************************************************************************************************************"""




"""**********************************BEGIN POST-PROCESSING STAGE: *****************************************************
****************************************************************************************************************"""



# -------------------------------------------------------------------------- #
# ------------------------ CREATE SPLIT, FILES, ... ------------------------ #
# -------------------------------------------------------------------------- #
print '\n\n'
#dataset_final = json.load(open('', 'rb'))
result_final_HQ = {node_id: value['HQ'] for node_id, value in dataset_final.iteritems()}


# ---------------------- EXTRACT HQ SOUNDS --------------------- #
all_ids_HQ = []
for key, value in result_final_HQ.iteritems():
        all_ids_HQ += value
all_ids_HQ = set(all_ids_HQ)

sounds_with_labels_HQ = {sound_id:[] for sound_id in all_ids_HQ}
for node_id in result_final_HQ:
    for s in result_final_HQ[node_id]:
        sounds_with_labels_HQ[s].append(node_id)

# how many sounds with multiple labels
print 'Total amount of HQ sounds with more than one label: {0} samples'.format(
    len([1 for sound_id in sounds_with_labels_HQ if 
         len(sounds_with_labels_HQ[sound_id])>1]))

print 'Total Number of HQ labeled sounds: {}'.format(len(sounds_with_labels_HQ))


# --------------------------------------------------------------- #

# --------------------- SPLIT DEV EVAL HQ ------------------------#
print '\n SPLIT HQ \n'

# STRUCTURE DATA, SPLIT SINGLE/MULTIPLE LABELED SOUNDS
sounds_single = {s:sounds_with_labels_HQ[s] for s in sounds_with_labels_HQ if len(sounds_with_labels_HQ[s])==1}
sounds_multiple = {s:sounds_with_labels_HQ[s] for s in sounds_with_labels_HQ if len(sounds_with_labels_HQ[s])>1}

data_single = {r:[] for r in result_final_HQ}
for s in sounds_single:
    data_single[sounds_single[s][0]].append(s)

print 'Number of single labeled HQ sounds: {0}'.format(len(sounds_single))
    
data_multiple = {r:[] for r in result_final_HQ}
for s in sounds_multiple:
    for i in sounds_multiple[s]: 
        data_multiple[i].append(s)

print 'Number of multi-labeled HQ sounds: {0}'.format(len(sounds_multiple))

# ORDER BY DURATION
data_single_dur = {r:sorted([(s, data_mapping[str(s)]['duration']) for s in data_single[r]], key=lambda c:c[1]) for r in data_single}
data_multiple_dur = {r:sorted([(s, data_mapping[str(s)]['duration']) for s in data_multiple[r]], key=lambda c:c[1]) for r in data_multiple}

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
            
## RANDOMLY ADDING MULTIPLE LABELED WITH RATIO 7:3
data_dev_HQ = data_single_dev
data_eval = data_single_eval
for idx, s in enumerate(sounds_multiple):
    if rule73[idx%len(rule73)] == 'dev':
        for node_id in sounds_multiple[s]:
            data_dev_HQ[node_id].append(s)
    elif rule73[idx%len(rule73)] == 'eval':
        for node_id in sounds_multiple[s]:
            data_eval[node_id].append(s)

# EXPORT DATASET
ontology_by_id = {o['id']:o for o in data_onto}
dataset_dev_HQ = [{'name': ontology_by_id[node_id]['name'], 
                'audioset_id': node_id,
                'sound_ids': data_dev_HQ[node_id],
               } for node_id in data_dev_HQ]
dataset_eval = [{'name': ontology_by_id[node_id]['name'], 
                'audioset_id': node_id,
                'sound_ids': data_eval[node_id],
               } for node_id in data_eval]

        
# --------------------------------------------------------------- #

# --------------------- ADD LQ TO DEV SET ------------------------#
print '\n ADD LQ TO DEV SET'

data_dev = copy.deepcopy(data_dev_HQ)
#for node_id in data_dev.keys():
#    data_dev[node_id] += dataset_final[node_id]['LQ']
data_dev_LQ = {node_id: value['LQ'] for node_id, value in dataset_final.iteritems()}

for node_id, value in dataset_final.iteritems():
    if 'LQprior' not in value:
        value['LQprior'] = []
data_dev_LQpior = {node_id: value['LQprior'] for node_id, value in dataset_final.iteritems()}

dataset_dev_LQ = [{'name': ontology_by_id[node_id]['name'], 
                'audioset_id': node_id,
                'sound_ids': dataset_final[node_id]['LQ'],
               } for node_id in dataset_final]


# ---------------------------------------------------------------- #

# ------------------------ SELECT LQ SET ------------------------- #
MAX_NUM_SOUND_DEV = 300
# ADD FIRST LQprior
for node_id in data_dev.keys():
    num_to_add = min(MAX_NUM_SOUND_DEV - len(data_dev[node_id]), len(data_dev_LQpior[node_id]))
    data_dev[node_id] += data_dev_LQpior[node_id][:num_to_add]

# FILTER OUT LQprior from LQ
data_dev_LQ_wo_prior = {}
for node_id in data_dev_LQ:
    data_dev_LQ_wo_prior[node_id] = list(set(data_dev_LQ[node_id])-set(data_dev_LQpior[node_id]))

# ORDER BY NUM DOWNLOADS
for node_id in data_dev_LQ_wo_prior.keys():
    ll = []
    for fs_id in data_dev_LQ_wo_prior[node_id]:
        try:
            if data_mapping[str(fs_id)]['num_downloads']:
                ll.append((fs_id, data_mapping[str(fs_id)]['num_downloads']))
            else:
                ll.append((fs_id, 0))
        except:
            ll.append((fs_id, 0))
    freesound_ids_with_num_downloads = sorted(ll, key=lambda x: x[1], reverse=True)
    data_dev_LQ_wo_prior[node_id] = [fs_id_num_downloads[0] for fs_id_num_downloads in freesound_ids_with_num_downloads]

# ADD LQ TO DEV SET UNTIL REACHING MAX 300 SOUNDS
for node_id in data_dev.keys():
    num_to_add = min(MAX_NUM_SOUND_DEV - len(data_dev[node_id]), len(data_dev_LQ_wo_prior[node_id]))
    data_dev[node_id] += data_dev_LQ_wo_prior[node_id][:num_to_add]
    
dataset_dev = [{'name': ontology_by_id[node_id]['name'], 
                'audioset_id': node_id,
                'sound_ids': data_dev[node_id],
               } for node_id in data_dev]


# ---------------------------------------------------------------- #

# -------------------- REMOVE SOME CATEGORIES -------------------- #
print '\n FILTER CATEGORIES \n'

sounds_left = []
for idx in range(len(dataset_dev)):
    sounds_left += dataset_dev[idx]['sound_ids']
    sounds_left += dataset_eval[idx]['sound_ids']
print 'Number of sounds before filtering: {0}'.format(len(set(sounds_left)))

category_id_to_remove = ['/m/0c1dj', '/m/07phxs1', '/m/02rr_', '/m/07s0s5r', '/m/0l14qv', '/m/05jcn', '/m/025l19', '/m/01b9nn', '/m/01jnbd', '/m/05mxj0q', '/m/06mb1', '/m/02hnl', '/m/02zsn', '/m/07r660_']

dataset_dev_filter = [d for d in dataset_dev if d['audioset_id'] not in category_id_to_remove]
dataset_eval_filter = [d for d in dataset_eval if d['audioset_id'] not in category_id_to_remove]

nb_labels_left = sum([len(d['sound_ids']) for d in dataset_dev_filter] + [len(d['sound_ids']) for d in dataset_eval_filter])

print 'Number of categories left: {0}'.format(len(dataset_dev_filter))

print 'Number of labels left: {0}'.format(nb_labels_left)

sounds_left = []
for idx in range(len(dataset_dev_filter)):
    sounds_left += dataset_dev_filter[idx]['sound_ids']
    sounds_left += dataset_eval_filter[idx]['sound_ids']
    
for aso_id in category_id_to_remove:
    del data_dev[aso_id]
    del data_dev_HQ[aso_id]
    del data_dev_LQ[aso_id]
    del data_dev_LQpior[aso_id]
    del data_eval[aso_id]
    
print 'Number of sounds left: {0}'.format(len(set(sounds_left)))


# ---------------------------------------------------------------- #

# -------------- REMOVE SOUND WITH MULTIPLE LABELS --------------- #
print '\n REMOVE MULTILABELED SOUNDS \n'
sound_to_remove = [s for s in sounds_left if sounds_left.count(s)>1]
for aso_id in data_dev.keys():
    for s in sound_to_remove:
        if s in data_dev[aso_id]:
            data_dev[aso_id].remove(s)
        if s in data_dev_HQ[aso_id]:
            data_dev_HQ[aso_id].remove(s)
        if s in data_dev_LQ[aso_id]:
            data_dev_LQ[aso_id].remove(s)
        if s in data_dev_LQpior[aso_id]:
            data_dev_LQpior[aso_id].remove(s)
        if s in data_eval[aso_id]:
            data_eval[aso_id].remove(s)

dataset_dev = [{'name': ontology_by_id[node_id]['name'], 
                'audioset_id': node_id,
                'sound_ids': data_dev[node_id],
               } for node_id in data_dev]

dataset_eval = [{'name': ontology_by_id[node_id]['name'], 
                'audioset_id': node_id,
                'sound_ids': data_eval[node_id],
               } for node_id in data_eval]
      

# ---------------------------------------------------------------- #

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

def sorted_occurrences_labels(data_dev_HQ, data_dev_LQ, data_dev_LQpior, data_dev, data_eval, ontology):
    """
    Create the worksheet with the number of sounds in each category of the ASO 
    Arguments:  - result from previous stage, e.g. result_leaves
                - ontology from json file
    """
    ontology_by_id = {o['id']:o for o in ontology}
    category_occurrences = []
    total_sounds = 0
    for node_id in data_dev_HQ.keys():
        nb_sample_dev_HQ = len(data_dev_HQ[node_id])
        nb_sample_dev_LQ = len(data_dev_LQ[node_id])
        nb_sample_eval = len(data_eval[node_id])
        nb_sample_dev = len(data_dev[node_id])
        nb_sample_dev_LQ_prior = len(data_dev_LQpior[node_id])
        total_sounds += nb_sample_dev + nb_sample_eval
        # get the names of parents (if several path, take one only and add (MULTIPLE PARENTS))
        all_parents = list(get_all_parents(node_id, ontology))
        if len(all_parents) > 1:
            names = ' > '.join(all_parents[0]+[ontology_by_id[node_id]['name']]) + ' (MULTIPLE PARENTS)'
        else:
            names = ' > '.join(all_parents[0]+[ontology_by_id[node_id]['name']])
        category_occurrences.append((names, node_id, nb_sample_dev_HQ, nb_sample_dev_LQ, nb_sample_dev_LQ_prior, nb_sample_dev, nb_sample_eval))
    category_occurrences = sorted(category_occurrences, key=lambda oc: oc[0])
    category_occurrences.append(('name', 'id', 'num dev HQ', 'num dev LQ', 'num dev LQ prior', 'num dev final', 'num eval'))
    category_occurrences.append(('Total number of sounds in final dataset', '', total_sounds, '', '', '', ''))
    category_occurrences.reverse()
    
    workbook = xlsxwriter.Workbook(FOLDER_DATA + 'list_categories_dataset_draft.xlsx')
    worksheet = workbook.add_worksheet('list categories')
    
    for idx, obj in enumerate(category_occurrences):
        worksheet.write(idx, 0, obj[0])
        worksheet.write(idx, 1, obj[1])
        worksheet.write(idx, 2, obj[2])
        worksheet.write(idx, 3, obj[3])
        worksheet.write(idx, 4, obj[4])
        worksheet.write(idx, 5, obj[5])
        worksheet.write(idx, 6, obj[6])
#    print '\n'
#    print 'Audio Set categories with their number of audio samples:\n'
#    for i in category_occurrences:
#        print str(i[0]).ljust(105) + str(i[1])


### WRITE EXCEL FILE ###
sorted_occurrences_labels(data_dev_HQ, data_dev_LQ, data_dev_LQpior, data_dev, data_eval, data_onto)


# --------------------------------------------------------------- #

# ---------------------- SPLIT LICENSE FILES -------------------- #
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

license_file = open(FOLDER_DATA + 'licenses_dev.txt', 'w')
license_file.write("This dataset uses the following sounds from Freesound:\n\n")
license_file.write("to access user page:  http://www.freesound.org/people/<username>\n")
license_file.write("to access sound page: http://www.freesound.org/people/<username>/sounds/<soundid>\n\n")
license_file.write("'<file name>' with ID <soundid> by <username> [<license>]\n\n")
for sound_id in sound_ids_dev:
    sound = data_mapping[str(sound_id)]
    name = sound['name'].encode('utf-8').replace('\r', '')
    username = sound['username'].encode('utf-8').replace('\r', '')
    license_file.write("'{0}' with ID {1} by {2} [CC-{3}]\n"
                       .format(name, sound_id, username, sound['license'].split('/')[-3].upper()))
license_file.close()

license_file = open(FOLDER_DATA + 'licenses_eval.txt', 'w')
license_file.write("This dataset uses the following sounds from Freesound:\n\n")
license_file.write("to access user page:  http://www.freesound.org/people/<username>\n")
license_file.write("to access sound page: http://www.freesound.org/people/<username>/sounds/<soundid>\n\n")
license_file.write("'<file name>' with ID <soundid> by <username> [<license>]\n\n")
for sound_id in sound_ids_eval:
    sound = data_mapping[str(sound_id)]
    name = sound['name'].encode('utf-8').replace('\r', '')
    username = sound['username'].encode('utf-8').replace('\r', '')
    license_file.write("'{0}' with ID {1} by {2} [CC-{3}]\n"
                       .format(name, sound_id, username, sound['license'].split('/')[-3].upper()))
license_file.close()


# --------------------------------------------------------------- #

# -------------------------- CREATE CSV ------------------------- #
try:
    merge = json.load(open(FOLDER_DATA + 'json/merge_categories.json', 'rb'))
except:
    raise Exception('CREATE THE FILE "merge_categories.json"')
node_id_parent = {}
for d in merge:
    for dd in merge[d]:
        node_id_parent[dd] = d
        
#ontology = json.load(open('ontology/ontology.json', 'rb'))
#ontology_by_id = {o['id']:o for o in ontology}
sounds_A = [] # sounds for dataset A
sounds_B = [] # sounds for dataset B

import csv
with open(FOLDER_DATA + 'dataset_dev.csv', 'wb') as f:
    writer = csv.writer(f)
    for d in dataset_dev:
        for sound_id in d['sound_ids']:
            if sound_id in data_dev_HQ[d['audioset_id']]:
                quality = 1
            elif sound_id in data_dev_LQ[d['audioset_id']] or sound_id in data_dev_LQpior[d['audioset_id']]:
                quality = 0
            sounds_A.append((sound_id, data_mapping[str(sound_id)]['duration']))
            try:
                writer.writerow([sound_id, d['audioset_id'], d['name'], node_id_parent[d['audioset_id']], ontology_by_id[node_id_parent[d['audioset_id']]]['name'], quality])
                sounds_B.append((sound_id, data_mapping[str(sound_id)]['duration']))
            except:
                writer.writerow([sound_id, d['audioset_id'], d['name'], None, None, quality])

with open(FOLDER_DATA + 'dataset_eval.csv', 'wb') as f:
    writer = csv.writer(f)
    for d in dataset_eval:
        for sound_id in d['sound_ids']:
            sounds_A.append((sound_id, data_mapping[str(sound_id)]['duration']))
            try:
                writer.writerow([sound_id, d['audioset_id'], d['name'], node_id_parent[d['audioset_id']], ontology_by_id[node_id_parent[d['audioset_id']]]['name']])
                sounds_B.append((sound_id, data_mapping[str(sound_id)]['duration']))
            except:
                writer.writerow([sound_id, d['audioset_id'], d['name'], None, None])

print 'Total duration of the dataset A: {0} secondes'.format(sum([s[1] for s in list(set(sounds_A))]))
print 'Total duration of the dataset B: {0} secondes'.format(sum([s[1] for s in list(set(sounds_B))]))
print 'Total of classes in dataset B: {0}'.format(len(merge))

all_ids = [s[0] for s in sounds_A]
json.dump(all_ids, open(FOLDER_DATA + 'all_freesound_ids.json', 'w'))
            
# --------------------------------------------------------------- #
