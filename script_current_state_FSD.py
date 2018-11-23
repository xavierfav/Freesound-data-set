import sys
import json
import numpy as np
import copy
import matplotlib.pyplot as plt
import pprint


# DIY

"""
This script takes a FSD dump as input, and computes stats about the current state of the annotation per class
Specifically, for every class:
1-number of GT (ie PPx2 and PNPx2)
2-number of annotations that have been voted by humans, but have not reached a GT of any kind (ie no agreement)
3-number of virgin candidates


2,3 are the annotations that could eventually complement what we already have curated, depending on the Quality Estimate
of every class

"""

FLAG_PLOT = False

"""
*****************************************************************************CONSTANTS THAT DEFINE THE STUDY
"""

# nice to compute this as class-dependent
# number of votes that are needed to reach agreement, on average, for a gtless annotation
# TODO compute general average for the 396 and based on it, decide these 2
FACTOR_AGREE_GTLESS = 1.5
# number of votes that are needed to reach agreement, on average, for a virgin annotation
FACTOR_AGREE_VIRGIN = 3.0
# lets consider a bit more of needed votes to be safe (just in case)
FACTOR_FLEX = 1.15

# we can do packs of roughly 10 categories. it will depend on the siblings and coherence in the groups that can be made.
# 1 session of 1 class are 66 useful votes. 10 sessions are 660 votes.
# This can be done in 5 h easily, with rests, carefully, FAQ n FS, 25E
# of course this depends on the difficulty. Easier classes are faster and viceversa
NB_VOTES_PACK_PERSON = 660.0

# 5 hours of work at 5 euros/hour. This may be ok for UPF-people. But in Freesound we should give more?
PRICE_PACK_PERSON = 27
# 25 /10 / 72 = 3.5 cents per click
# 30 /10 / 72 = 4.17 cents per click. maybe give 30 then, so that it is a bit more than F8

mode = 'ALL_CATS'
# mode = 'BEGINNER'
# mode = 'ADVANCED'
# mode = 'VALID_LEAF'

# DURATION_MODE = 'ALL'
# DURATION_MODE = 'SHORT'
DURATION_MODE = 'MID'
# DURATION_MODE = 'LONG'
# DURATION_MODE = 'MID_n_LONG'


MINLEN = 0.3  # duration
MAXLEN = 30.0
FOLDER_DATA = 'kaggle3/'
MIN_VOTES_CAT = 70  # minimum number of votes per category to produce a QE.
# TARGET_SAMPLES = 130
# at August 7th
TARGET_SAMPLES = 300
# TARGET_SAMPLES = 320

# in kaggle we have minimum 84 samples/class, and on average 130. we have to significantly improve this
# audioset has minimum of 120
# let's say 125 as a target for annotation, then we can lower it to 120 for acceptance.

NB_VOTES_PER_SESSION = 66.0
NB_SESSIONS_PER_PACK = 10.0   # this is 5 hours of work
NB_PACKS_PER_WEEK = 4.5       # to have part-time job
NB_SUBJECTS_AVAILABLE = 4.5   # assuming 5 annotators during the august

print('\nParams for simulation=')
pprint.pprint(mode, width=1, indent=4)
pprint.pprint(DURATION_MODE, width=1, indent=4)
pprint.pprint(TARGET_SAMPLES, width=1, indent=4)
pprint.pprint(FACTOR_FLEX, width=1, indent=4)


"""load initial data with votes, clip duration and ontology--------------------------------- """

# this the result of the mapping from FS sounds to ASO.
# a dict with 268k keys (the fs_ids) and values include metadata for every sound)
# 268k sounds with basic metadata and their corresponding ASO id.
# useful to get the duration of every sound
# try:
#     with open(FOLDER_DATA + 'json/FS_sounds_ASO_postIQA.json') as data_file:
#         data_mapping = json.load(data_file)
# except:
#     raise Exception(
#         'CHOOSE A MAPPING FILE AND ADD IT TO ' + FOLDER_DATA + 'json/ FOLDER (THE FILE INCLUDE DURATION INFORMATION NEEDED)')

# UPDATE: the above does not contain the sounds added on August 3rd.
# We need to get this info
# for every id that is in data_votes_raw and is not in data_mapping (ie los 30k nuevos que se cargaron con el new mapping),
# retrieve duration with FS API
# los otros 40k old no aparecen porque no tienen candidates annotations. luego estan en platform, pero no en dump.
# done in script aside. the info for the 297291 files is in FS_sounds_ASO_postIQA_2018_Aug_08.json
try:
    with open(FOLDER_DATA + 'json/FS_sounds_ASO_postIQA_2018_Aug_08.json') as data_file:
        data_mapping = json.load(data_file)
except:
    raise Exception(
        'CHOOSE A MAPPING FILE AND ADD IT TO ' + FOLDER_DATA + 'json/ FOLDER (THE FILE INCLUDE DURATION INFORMATION NEEDED)')
# this mapping has 297291 sounds, ie old 268k + 30k new

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
    # with open(FOLDER_DATA + 'json/votes_dumped_2018_Aug_08.json') as data_file:
    # with open(FOLDER_DATA + 'json/votes_dumped_2018_Nov_07.json') as data_file:


    with open(FOLDER_DATA + 'json/votes_dumped_2018_Nov_21.json') as data_file:
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




# sanity checks right after loading the dump
# gt_sounds_cam = [item for item in data_votes_raw['/m/0dv5r']['PP'] if data_votes_raw['/m/0dv5r']['PP'].count(item) > 1]
# num_gt_sounds_cam = len(gt_sounds_cam)/2.0
#
# gt_sounds_ba = [item for item in data_votes_raw['/m/03dnzn']['PP'] if data_votes_raw['/m/03dnzn']['PP'].count(item) > 1]
# num_gt_sounds_ba = len(gt_sounds_ba)/2.0
#
#
#
"""
*****************************************************************************FUNCTIONS
"""

def apply_duration_filter(data_in, _minlen, _maxlen):
    """
    Creates a deep copy of the data_in, and applies duration filters to return only the files within the duration

    :param data_in: dict with all the sounds and their votes
    :param data_out: dict keeping only the sounds that last between [_minlen, _maxlen)
    :param _minlen:
    :param _maxlen:
    :return: data_out
    """
    # create data_out with keys with catids, the same type of keys for every catid, and empty lists
    data_out = copy.deepcopy(data_in)
    for catid, votes in data_out.iteritems():
        # data_out[catid].clear()
        data_out[catid]['PP'] = []
        data_out[catid]['PNP'] = []
        data_out[catid]['NP'] = []
        data_out[catid]['U'] = []
        data_out[catid]['candidates'] = []

    for catid, votes in data_in.iteritems():
        for fsid in votes['PP']:
            try:
                if (data_mapping[str(fsid)]['duration'] < _maxlen) and (data_mapping[str(fsid)]['duration'] >= _minlen):
                    data_out[catid]['PP'].append(fsid)
            except:
                print('=========================there is a fs_id {0} not found in data_mapping'.format(fsid))


        for fsid in votes['PNP']:
            try:
                if (data_mapping[str(fsid)]['duration'] < _maxlen) and (data_mapping[str(fsid)]['duration'] >= _minlen):
                    data_out[catid]['PNP'].append(fsid)
            except:
                print('=========================there is a fs_id {0} not found in data_mapping'.format(fsid))


        for fsid in votes['NP']:
            # if fsid == 351266:
            #     j=9
            try:
                if (data_mapping[str(fsid)]['duration'] < _maxlen) and (data_mapping[str(fsid)]['duration'] >= _minlen):
                    data_out[catid]['NP'].append(fsid)
            except:
                print('=========================there is a fs_id {0} not found in data_mapping'.format(fsid))


        for fsid in votes['U']:
            try:
                if (data_mapping[str(fsid)]['duration'] < _maxlen) and (data_mapping[str(fsid)]['duration'] >= _minlen):
                    data_out[catid]['U'].append(fsid)
            except:
                print('=========================there is a fs_id {0} not found in data_mapping'.format(fsid))


        for fsid in votes['candidates']:
            try:
                if (data_mapping[str(fsid)]['duration'] < _maxlen) and (data_mapping[str(fsid)]['duration'] >= _minlen):
                    data_out[catid]['candidates'].append(fsid)
            except:
                print('=========================there is a fs_id {0} not found in data_mapping'.format(fsid))


    return data_out


def check_gt_v2(_group, _fsid, _catid, _votes, _fsids_assigned_cat, _data):
    """ # check if fsid has GT within a given group (PP,PNP,NP,U) of a category given by catid
    # if it does, add it to assigned fsids and send it to the corresponding group in data
    """
    assigned = False
    if _votes[_group].count(_fsid) > 1:
        if _fsid not in _fsids_assigned_cat:
            # more than one vote, and first time we see it (never been assigned yet)
            _data[_catid][_group + 'gt'].append(_fsid)
            _fsids_assigned_cat.append(_fsid)
            assigned = True
        else:
            # there is more than one vote, hence it is gt, but it has been already assigned before, hence flag it
            assigned = True
    return _data, _fsids_assigned_cat, assigned


def plot_barplot(data, x_labels, y_label, fig_title, MAX_VERT_AX, threshold=None):
    ind = np.arange(len(data))  # the x locations for the LEFT bars
    width = 0.35  # the width of the bars: can also be len(x) sequence
    axes = [-0.5, len(data), 0, MAX_VERT_AX]

    fig, ax = plt.subplots()
    # fig = plt.figure()
    # ax = fig.add_subplot(111)
    p1 = ax.bar(ind, data, width=width, color='blue', edgecolor="none")
    for tt in range(0, ind[-1], 100):
        ax.axvspan(tt, tt+49, alpha=0.1, color='red')
    # horizontal line indicating the threshold
    if threshold:
        plt.plot([0, 400], [threshold, threshold], "k--", linewidth=2)
    plt.xticks(fontsize=7, rotation=45)
    # ax.set_xticks(ind + width)
    # ax.set_xticklabels(x_labels)
    plt.xticks(ind, x_labels)
    ax.set_ylabel(y_label)
    ax.set_title(fig_title)
    # plt.yticks(np.arange(0, 81, 10))
    # ax.legend((p1[0]), legenda)
    plt.axis(axes)
    ax.yaxis.grid(True)
    # plt.grid(True)
    plt.show()


def plot_barplot_grouped2(data_left, data_right, x_labels, y_label, fig_title, legenda, MAX_VERT_AX, threshold=None):
    ind = np.arange(len(data_left))  # the x locations for the LEFT bars
    width = 0.35  # the width of the bars: can also be len(x) sequence
    axes = [-0.5, len(data_left), 0, MAX_VERT_AX]

    fig, ax = plt.subplots()
    # fig = plt.figure()
    # ax = fig.add_subplot(111)
    p1 = ax.bar(ind, data_left, width=width, color='blue', edgecolor="none")
    p2 = ax.bar(ind + width, data_right, width=width, color='cyan', edgecolor="none")
    # horizontal line indicating the threshold
    if threshold:
        plt.plot([0, 48], [threshold, threshold], "k--", linewidth=2)
    plt.xticks(fontsize=7, rotation=45)
    # ax.set_xticks(ind + width)
    # ax.set_xticklabels(x_labels)
    plt.xticks(ind + width, x_labels)
    ax.set_ylabel(y_label)
    ax.set_title(fig_title)
    # plt.yticks(np.arange(0, 81, 10))
    ax.legend((p1[0], p2[0]), legenda)
    plt.axis(axes)
    ax.yaxis.grid(True)
    # plt.grid(True)
    plt.show()


def plot_barplot_grouped3(data_left, data_middle, data_right, x_labels, y_label, fig_title, legenda, MAX_VERT_AX, threshold=None):
    ind = np.arange(len(data_left))  # the x locations for the LEFT bars
    width = 0.25  # the width of the bars: can also be len(x) sequence
    axes = [-0.5, len(data_left), 0, MAX_VERT_AX]

    fig, ax = plt.subplots()
    # fig = plt.figure()
    # ax = fig.add_subplot(111)
    p1 = ax.bar(ind, data_left, width=width, color='blue', edgecolor="none")
    p2 = ax.bar(ind + width, data_middle, width=width, color='cyan', edgecolor="none")
    p3 = ax.bar(ind + 2*width, data_right, width=width, color='yellow', edgecolor="none")
    for tt in range(0, ind[-1], 100):
        ax.axvspan(tt, tt+49, alpha=0.1, color='red')
    # horizontal line indicating the threshold
    if threshold:
        plt.plot([0, 400], [threshold, threshold], "k--", linewidth=1)
    plt.xticks(fontsize=6, rotation=45)
    # ax.set_xticks(ind + width)
    # ax.set_xticklabels(x_labels)
    plt.xticks(ind + width, x_labels)
    ax.set_ylabel(y_label)
    ax.set_title(fig_title)
    # plt.yticks(np.arange(0, 81, 10))
    ax.legend((p1[0], p2[0], p3[0]), legenda)
    plt.axis(axes)
    ax.yaxis.grid(True)
    # plt.grid(True)
    plt.show()

    # put the QE on top of the bars, to estimate the ratio of gtless and virgin visually.


def sort_all_by_criteria(names_all_cats, nb_sounds_valid, nb_sounds_gtless, nb_sounds_virgin, idx):
    """
    variables to plot, order them according to an idx that reflects some criteria, for clarity in the plot
    :param names_all_cats:
    :param nb_sounds_valid:
    :param nb_sounds_gtless:
    :param nb_sounds_virgin:
    :param idx:
    :return:
    """
    # classes ordered by number of XXXXX samples
    names_all_cats_sorted = list(names_all_cats[val] for val in idx)
    nb_sounds_valid_sorted = list(nb_sounds_valid[val] for val in idx)
    nb_sounds_gtless_sorted = list(nb_sounds_gtless[val] for val in idx)
    nb_sounds_virgin_sorted = list(nb_sounds_virgin[val] for val in idx)
    return names_all_cats_sorted, nb_sounds_valid_sorted, nb_sounds_gtless_sorted, nb_sounds_virgin_sorted


"""
*****************************************************************************BEGIN SCRIPT
"""

""" # report initial stats on the dump*************************************"""
"""******************************************************************************************************************"""

# sanity check: total number of mapped sounds and total number of automatically generated annotations
accum_fsids = []
for catid, votes in data_votes_raw.iteritems():
    # accum_fsids.append(votes['candidates'])
    accum_fsids += votes['candidates']
print('Number of sounds in the dump: %d' % len(set(accum_fsids)))
print('Number of automatically generated annotations in the dump: %d' % len(accum_fsids))
print('Number of categories from the dump: %d' % len(data_votes_raw))

nb_gt = 0
for cat_id, groups in data_votes_raw.iteritems():
    # beware, if they are 3 or 4, the y are counted more.

    for fs_id in groups['candidates']:
        if groups['PP'].count(fs_id) > 1:
            nb_gt += 1
        elif groups['PNP'].count(fs_id) > 1:
            nb_gt += 1

    # the following yields very similar results
    # gt_soundsPP = [item for item in groups['PP'] if groups['PP'].count(item) > 1]
    # nb_gt_PP = len(gt_soundsPP)/2.0
    #
    # # repeat for PNP
    # gt_soundsPNP = [item for item in groups['PNP'] if groups['PNP'].count(item) > 1]
    # nb_gt_PNP = len(gt_soundsPNP)/2.0
    #
    # # add
    # nb_gt += nb_gt_PP
    # nb_gt += nb_gt_PNP

print('\nNumber of ground truth PP*2 and PNP*2 from the dump: %d' % nb_gt)

a=9

# sanity checks right after loading the dump
# gt_sounds_cam = [item for item in data_votes_raw['/m/0dv5r']['PP'] if data_votes_raw['/m/0dv5r']['PP'].count(item) > 1]
# num_gt_sounds_cam = len(gt_sounds_cam)/2.0
#
# gt_sounds_ba = [item for item in data_votes_raw['/m/03dnzn']['PP'] if data_votes_raw['/m/03dnzn']['PP'].count(item) > 1]
# num_gt_sounds_ba = len(gt_sounds_ba)/2.0
#



""" # remove unwanted sounds from specific categories before doing anything else*************************************"""
"""******************************************************************************************************************"""
# First off, we may need to do some pre-processing to remove some sounds we already now they are wrong
# # remove the sounds from data_votes_raw
data_votes = copy.deepcopy(data_votes_raw)

# empty for now



# lets compute the QE here, considering all the sounds
# shall we do it before/after the manual removal of sounds
# for every category compute QE here number of votes len(PP) + len(PNP) / all
# QE should only be computed if there are more than MIN_VOTES_CAT votes. else not reliable, and hence defined to 0
for catid, votes in data_votes.iteritems():
    if (len(votes['PP']) + len(votes['PNP']) + len(votes['NP']) + len(votes['U'])) >= MIN_VOTES_CAT:
        data_votes[catid]['QE'] = (len(votes['PP']) + len(votes['PNP'])) / float(
            len(votes['PP']) + len(votes['PNP']) + len(votes['NP']) + len(votes['U']))
    else:
        data_votes[catid]['QE'] = 0

# we keep the QE just in case, for plots and/or diagnosis

""" # apply initial constraints for the study*************************************"""
"""******************************************************************************************************************"""

# FILTERS TO APPLY FOR SIMPLICITY
# 0-grab only de 396 valid categories
# 1-lets focus on the leaf categories for now (simplest case)
# 2-split into short, mid and long sounds. Focus on mid

# FILTER 0: Consider only valid categories, ie those that are omitted = False in the database
data_votes_v = {o: data_votes[o] for o in data_votes if o in data_info_valid}
print 'Number of valid categories in the dump: ' + str(len(data_votes_v))

# FILTER 1: Consider only leaf categories: 474 out of the initial 632
# for o in data_votes. o = catid
# create a dict of dicts. The latter are key=o, and value the actual value (data_votes[o])
data_votes_l = {o: data_votes[o] for o in data_votes if len(data_onto_by_id[o]['child_ids']) < 1}
print 'Number of leaf categories in the dump: ' + str(len(data_votes_l))
# this implies mixture of both beginer and advanced

# FILTER 1.1: Consider only BEGINNER and VALID categories:
data_votes_vb = {o: data_votes[o] for o in data_votes if o in data_info_valid and data_info_valid[o]['beginner_task'] == True}
print 'Number of valid beginner categories in the dump: ' + str(len(data_votes_vb))

# FILTER 1.2: Consider only ADVANCED and VALID categories:
# we compute this as the complementary of the privious one
# but BEWARE: there is now a few classes where both fields are set to False cause they are not open to the public
data_votes_va = {o: data_votes[o] for o in data_votes if o in data_info_valid and data_info_valid[o]['beginner_task'] == False}
print 'Number of valid advanced categories in the dump: ' + str(len(data_votes_va))

# apply FILTER 0 and 1: by taking the union of the above (valid and leaf)
data_votes_vl = {o: data_votes[o] for o in data_votes if o in data_votes_v and o in data_votes_l}
print 'Number of valid AND leaf categories in the dump: ' + str(len(data_votes_vl))


# FILTER 2: Apply duration filter: Within the 474 categories:
# short sounds [0:MINLEN)
# mid sounds [MINLEN: MAXLEN)
# long sounds [MAXLEN, inf)

# no more filters for now, we just want to know which data we have
# print()
# to carry out the study
# data_votes_study = data_votes_all
if mode == 'ALL_CATS':
    # the 396
    data_votes_select = data_votes_v
elif mode == 'BEGINNER':
    data_votes_select = data_votes_vb
elif mode == 'ADVANCED':
    data_votes_select = data_votes_va
elif mode == 'VALID_LEAF':
    # 296 valid leaves
    data_votes_select = data_votes_vl

# data_votes_mid = copy.deepcopy(data_votes_l)
data_votes_short = apply_duration_filter(data_votes_select, 0, MINLEN)
data_votes_mid = apply_duration_filter(data_votes_select, MINLEN, MAXLEN)
data_votes_long = apply_duration_filter(data_votes_select, MAXLEN, 95.0)
data_votes_all = data_votes_select
data_votes_midlong = apply_duration_filter(data_votes_select, MINLEN, 95.0)

# including NC-license for now

if DURATION_MODE == 'ALL':
    data_votes_study = data_votes_all
elif DURATION_MODE == 'SHORT':
    data_votes_study = data_votes_short
elif DURATION_MODE == 'MID':
    data_votes_study = data_votes_mid
elif DURATION_MODE == 'LONG':
    data_votes_study = data_votes_long
elif DURATION_MODE == 'MID_n_LONG':
    data_votes_study = data_votes_midlong




""" # Categorize the annotations/sounds in every category: as
-PPgt
-PNPgt
-NPgt
-Ugt
-gtless
-virgin
******************************************************************************************************************"""

# considering only sounds between  [MINLEN: MAXLEN): data_votes_study

# create data_state with keys with catids and empty dicts as values
data_state = copy.deepcopy(data_votes_study)
for catid, votes in data_state.iteritems():
    data_state[catid].clear()
    data_state[catid]['PPgt'] = []
    data_state[catid]['PNPgt'] = []
    data_state[catid]['NPgt'] = []
    data_state[catid]['Ugt'] = []
    data_state[catid]['gtless'] = []
    data_state[catid]['virgin'] = []


for catid, votes in data_votes_study.iteritems():
    # list to keep track of assigned fsids within a category, to achieve disjoint subsets of audio samples
    fsids_assigned_cat = []

    # to debug certain categories
    # if data_onto_by_id[catid]['name'] == 'Pizzicato':
    # if data_onto_by_id[catid]['name'] == 'Toothbrush':
    # if data_onto_by_id[catid]['name'] == 'Camera':
    # if data_onto_by_id[catid]['name'] == 'Bathtub (filling or washing)':
    #     a = 8

    # check GT in PP
    # check GT in the rest of the groups
    for fsid in votes['PP']:
        # search for GT in this group
        data_state, fsids_assigned_cat, assigned = check_gt_v2('PP', fsid, catid, votes, fsids_assigned_cat,
                                                                  data_state)
        if not assigned:
            data_state, fsids_assigned_cat, assigned = check_gt_v2('PNP', fsid, catid, votes, fsids_assigned_cat,
                                                                 data_state)
        if not assigned:
            data_state, fsids_assigned_cat, assigned = check_gt_v2('U', fsid, catid, votes, fsids_assigned_cat,
                                                                 data_state)
        if not assigned:
            data_state, fsids_assigned_cat, assigned = check_gt_v2('NP', fsid, catid, votes, fsids_assigned_cat,
                                                                 data_state)
        if not assigned:
            # no GT was found for the annotation (2 votes in the same group), in none of the groups
            # since it has at least one PP vote (there may have others, like PP + PNP (but no GT), we append to
            if fsid not in fsids_assigned_cat:
                data_state[catid]['gtless'].append(fsid)
                fsids_assigned_cat.append(fsid)

    # check GT in PNP
    # check GT in the remaining groups
    for fsid in votes['PNP']:

        data_state, fsids_assigned_cat, assigned = check_gt_v2('PNP', fsid, catid, votes, fsids_assigned_cat,
                                                                     data_state)
        if not assigned:
            data_state, fsids_assigned_cat, assigned = check_gt_v2('U', fsid, catid, votes, fsids_assigned_cat,
                                                                         data_state)
        if not assigned:
            data_state, fsids_assigned_cat, assigned = check_gt_v2('NP', fsid, catid, votes, fsids_assigned_cat,
                                                                         data_state)
        if not assigned:
            # no GT was found for the annotation (2 votes in the same group), in PNP U NP, but it could be in PP
            if fsid not in fsids_assigned_cat:
                # it does not have GT whatsoever. Yet it has a vote distribution, at least one PNP
                data_state[catid]['gtless'].append(fsid)
                fsids_assigned_cat.append(fsid)

    # check GT in U
    # check GT in the remaining groups
    for fsid in votes['U']:
        data_state, fsids_assigned_cat, assigned = check_gt_v2('U', fsid, catid, votes, fsids_assigned_cat,
                                                                     data_state)
        if not assigned:
            data_state, fsids_assigned_cat, assigned = check_gt_v2('NP', fsid, catid, votes, fsids_assigned_cat,
                                                                         data_state)
        if not assigned:
            # no GT was found for the annotation (2 votes in the same group), in U NP, but it could be in PP or PNP
            if fsid not in fsids_assigned_cat:
                # it does not have GT whatsoever. Yet it has a vote distribution, at least one U
                data_state[catid]['gtless'].append(fsid)
                fsids_assigned_cat.append(fsid)

    # check GT in NP
    # check GT in the remaining groups? no need to. already done in previous passes
    for fsid in votes['NP']:
        data_state, fsids_assigned_cat, assigned = check_gt_v2('NP', fsid, catid, votes, fsids_assigned_cat,
                                                                     data_state)
        # else: no need to. already done in previous passes
        if not assigned:
            # no GT was found for the annotation (2 votes in the same group), in NP, but it could be in PP or PNP or NP
            if fsid not in fsids_assigned_cat:
                # it does not have GT whatsoever. Yet it has a vote distribution, at least one NP
                data_state[catid]['gtless'].append(fsid)
                fsids_assigned_cat.append(fsid)

    # lastly, those sounds that have NEVER been voted for this catid
    data_state[catid]['virgin'] = [item for item in votes['candidates'] if item not in votes['PP'] and
                                         item not in votes['PNP'] and
                                         item not in votes['NP'] and
                                         item not in votes['U']]

    # =======================SANITY CHECKS===================================
    # sanity checks for duplicated sounds in GT groups,
    # disjoint sets and
    # also count of fsids in total, this is for every catid

    # sanity check: there should be no duplicated fsids within the groups of GT
    # even though there are some mistakes, they are analized sequentiallu, first called, first served.
    if (len(data_state[catid]['PPgt']) != len(set(data_state[catid]['PPgt'])) or
                len(data_state[catid]['PNPgt']) != len(set(data_state[catid]['PNPgt'])) or
                len(data_state[catid]['NPgt']) != len(set(data_state[catid]['NPgt'])) or
                len(data_state[catid]['Ugt']) != len(set(data_state[catid]['Ugt']))):
        print(data_onto_by_id[catid]['name'], catid)
        sys.exit('duplicates in the groups of GT in data_state')

    # sanity check: ALL groups in data_state should be disjoint
    if (list(set(data_state[catid]['PPgt']) & set(data_state[catid]['PNPgt'])) or
            list(set(data_state[catid]['PPgt']) & set(data_state[catid]['NPgt'])) or
            list(set(data_state[catid]['PPgt']) & set(data_state[catid]['Ugt'])) or
            list(set(data_state[catid]['PPgt']) & set(data_state[catid]['gtless'])) or
            list(set(data_state[catid]['PPgt']) & set(data_state[catid]['virgin'])) or
            list(set(data_state[catid]['PNPgt']) & set(data_state[catid]['NPgt'])) or
            list(set(data_state[catid]['PNPgt']) & set(data_state[catid]['Ugt'])) or
            list(set(data_state[catid]['PNPgt']) & set(data_state[catid]['gtless'])) or
            list(set(data_state[catid]['PNPgt']) & set(data_state[catid]['virgin'])) or
            list(set(data_state[catid]['NPgt']) & set(data_state[catid]['Ugt'])) or
            list(set(data_state[catid]['NPgt']) & set(data_state[catid]['gtless'])) or
            list(set(data_state[catid]['NPgt']) & set(data_state[catid]['virgin'])) or
            list(set(data_state[catid]['Ugt']) & set(data_state[catid]['gtless'])) or
            list(set(data_state[catid]['Ugt']) & set(data_state[catid]['virgin'])) or
            list(set(data_state[catid]['gtless']) & set(data_state[catid]['virgin']))):
        print(data_onto_by_id[catid]['name'], catid)
        sys.exit('data_state has not disjoint groups')

    # sanity check: number of sounds is equal in data_sounds (adding) and data_votes (concatenating groups and set)
    all_votes = data_votes_study[catid]['PP'] + data_votes_study[catid]['PNP'] + \
                data_votes_study[catid]['NP'] + data_votes_study[catid]['U'] + data_votes_study[catid]['candidates']
    nb_sounds_data_votes = len(set(all_votes))

    nb_sounds_data_state = (len(data_state[catid]['PPgt']) + len(data_state[catid]['PNPgt']) + \
                             len(data_state[catid]['NPgt']) + len(data_state[catid]['Ugt']) +
                            len(data_state[catid]['gtless']) + len(data_state[catid]['virgin']))
    # in theory no need for set neither in gtless nor virgin, but check out

    if nb_sounds_data_votes != nb_sounds_data_state:
        print(data_onto_by_id[catid]['name'], catid)
        sys.exit('number of sounds is not equal in data_state and data_votes')

# checked that the conversion from intial set of votes from the dump, to the keys in data_state is fine.
# Cases that do not match with the platform: for now it is ok
#



""" # plots**********************************************************************************************************"""
"""******************************************************************************************************************"""



# plot current status of what is to finalize per class
# -- # bar plot of number of sounds of each kind for every category----

names_all_cats = [data_onto_by_id[catid]['name'] for catid, sounds in data_state.iteritems()]
nb_sounds_PPgt = [len(groups['PPgt']) for catid, groups in data_state.iteritems()]
nb_sounds_PNPgt = [len(groups['PNPgt']) for catid, groups in data_state.iteritems()]
nb_sounds_valid = [i + j for i, j in zip(nb_sounds_PPgt, nb_sounds_PNPgt)]
nb_sounds_gtless = [len(groups['gtless']) for catid, groups in data_state.iteritems()]
nb_sounds_virgin = [len(groups['virgin']) for catid, groups in data_state.iteritems()]
qe_per_class = [data_votes[catid]['QE'] for catid, groups in data_state.iteritems()]

# TODO should be fine til here

# sort classes according to several criteria for plotting
# sort in descending order of valid samples
idx_valid = np.argsort(-np.array(nb_sounds_valid))
# sort in descending order of gtless samples; since they have a lot pending in the platform, this could be ok to stay in platform
idx_gtless = np.argsort(-np.array(nb_sounds_gtless))
# sort in descending order of virgin samples, this could be ok for F8
idx_virgin = np.argsort(-np.array(nb_sounds_virgin))

y_label = '# of audio samples'


if FLAG_PLOT:
    names_all_cats_sorted, nb_sounds_valid_sorted, nb_sounds_gtless_sorted, nb_sounds_virgin_sorted = sort_all_by_criteria(
        names_all_cats, nb_sounds_valid, nb_sounds_gtless, nb_sounds_virgin, idx_valid)

    legenda = ('valid', 'gtless', 'virgin')
    fig_title = 'number of samples per category - sorted by number of valid samples'
    plot_barplot_grouped3(nb_sounds_valid_sorted,
                          nb_sounds_gtless_sorted,
                          nb_sounds_virgin_sorted,
                          names_all_cats_sorted,
                          y_label,
                          fig_title,
                          legenda,
                          300,
                          threshold=TARGET_SAMPLES)

    names_all_cats_sorted, nb_sounds_valid_sorted, nb_sounds_gtless_sorted, nb_sounds_virgin_sorted = sort_all_by_criteria(
        names_all_cats, nb_sounds_valid, nb_sounds_gtless, nb_sounds_virgin, idx_gtless)

    fig_title = 'number of samples per category - sorted by number of gtless samples'
    plot_barplot_grouped3(nb_sounds_valid_sorted,
                          nb_sounds_gtless_sorted,
                          nb_sounds_virgin_sorted,
                          names_all_cats_sorted,
                          y_label,
                          fig_title,
                          legenda,
                          300,
                          threshold=TARGET_SAMPLES)

    names_all_cats_sorted, nb_sounds_valid_sorted, nb_sounds_gtless_sorted, nb_sounds_virgin_sorted = sort_all_by_criteria(
        names_all_cats, nb_sounds_valid, nb_sounds_gtless, nb_sounds_virgin, idx_virgin)

    fig_title = 'number of samples per category - sorted by number of virgin samples'
    plot_barplot_grouped3(nb_sounds_valid_sorted,
                          nb_sounds_gtless_sorted,
                          nb_sounds_virgin_sorted,
                          names_all_cats_sorted,
                          y_label,
                          fig_title,
                          legenda,
                          400,
                          threshold=TARGET_SAMPLES)



""" # print report***************************************************************************************************"""
"""******************************************************************************************************************"""

print("**************************************************Report for mode %s" % mode)

# need comments here
cats_accomplished_success = {}          # classes that already have TARGET_SAMPLES. ready to do the split tr/te
cats_estimated_success = {}             # classes that we estimate that MAY reach TARGET_SAMPLES, through annotation
cats_runout_content = {}                # classes that we have run out of content.


for catid, groups in data_state.iteritems():
    # they already have TARGET_SAMPLES
    if len(groups['PPgt']) + len(groups['PNPgt']) >= TARGET_SAMPLES:
        cats_accomplished_success[catid] = len(groups['PPgt']) + len(groups['PNPgt'])

    else:
        # they dont have TARGET_SAMPLES, but we estimate how much it can have with the QE (only if QE is well estimated)
        if data_votes[catid]['QE'] > 0:
            estimated_gt = len(groups['PPgt']) + len(groups['PNPgt']) + \
                           (len(groups['gtless']) + len(groups['virgin'])) * data_votes[catid]['QE']
            if estimated_gt >= TARGET_SAMPLES:
                cats_estimated_success[catid] = estimated_gt

    if len(groups['gtless']) + len(groups['virgin']) == 0:
        # there is no more content available, except if we improve the mapping and by doing it we gather some more
        cats_runout_content[catid] = len(groups['PPgt']) + len(groups['PNPgt'])

print("# how many cats have already TARGET_SAMPLES? (beware, unpopulated): %d" % len(cats_accomplished_success))
for idx, (cat_id,v) in enumerate(cats_accomplished_success.iteritems(), 1):
    print("%d - %-25s: sounds: %-3d" % (idx, data_onto_by_id[cat_id]['name'], v))

print("# how many cats can reach TARGET_SAMPLES with gtless and virgin, "
      "considering QE (including already accomplished): %d" % (len(cats_estimated_success) + len(cats_accomplished_success)))

print("# how many cats have run out of content: %d" % len(cats_runout_content))
for idx, (cat_id,v) in enumerate(cats_runout_content.iteritems(), 1):
    print("%d - %-25s: sounds: %-3d" % (idx, data_onto_by_id[cat_id]['name'], v))


"""new report"""
list_nb_gt_clips_class = []
list_catid_gt_clips_class = []
for catid, groups in data_state.iteritems():
    groups['gt_clips'] = len(groups['PPgt']) + len(groups['PNPgt'])
    # create corresponding lists with gt_clips and catids, for sorting
    list_nb_gt_clips_class.append(groups['gt_clips'])
    list_catid_gt_clips_class.append(catid)

# list_nb_gt_clips_class = [groups['gt_clips'] for catid, groups in data_state.iteritems()]
# list_catid_gt_clips_class = [catid for catid, groups in data_state.iteritems()]

# sort in descending order of gt_clips
idx_gt_clips = np.argsort(-np.array(list_nb_gt_clips_class))

# catids ordered by descending number of of gt_clips, to print metadata
list_catid_gt_clips_class_sorted = list(list_catid_gt_clips_class[val] for val in idx_gt_clips)

print('=Printing new report: desceding order of gt clips\n')
for idx_count, catid in enumerate(list_catid_gt_clips_class_sorted, 1):
    # print stuff
    print( "%d - %-25s: gt_clips: %-3d PPgt: %-3d PNPgt: %-3d gtless: %-3d unrated: %-4d QE: %1.3f" %
    (idx_count,
     data_onto_by_id[catid]['name'], data_state[catid]['gt_clips'], len(data_state[catid]['PPgt']),
     len(data_state[catid]['PNPgt']), len(data_state[catid]['gtless']), len(data_state[catid]['virgin']),
     data_votes[catid]['QE']))




#
# def print_status_data(data, ref):
#     # print('=Printing status after applying: {0}:'.format(ref))
#     for idx, (cat_id, v) in enumerate(data.items(), 1):
#         print("%d - %-25s: PPgt: %-3d PP: %-3d PNPgt: %-3d NPgt: %-3d Ugt: %-3d gtless: %-3d unvo: %-4d cand: %-4d QE: %1.3f" %
#               (idx, data_onto_by_id[cat_id]['name'], len(data[cat_id]['PPgt']),
#                len(data[cat_id]['PP']), len(data[cat_id]['PNPgt']),
#                len(data[cat_id]['NPgt']), len(data[cat_id]['Ugt']),
#                len(data[cat_id]['gtless']), len(data[cat_id]['unvo']),
#                len(data[cat_id]['cand']),  data[cat_id]['QE']))
#
#





# ===================
print("\n# how many gtless annotations do we have (ie voted but not gt yet): %d" % sum(nb_sounds_gtless))
print("# how many virgin annotations do we have: %d" % sum(nb_sounds_virgin))

# lets focus on classes where we did not reach the target
nb_sounds_gtless_left = [len(groups['gtless']) for catid, groups in data_state.iteritems() if catid not in cats_accomplished_success]
nb_sounds_virgin_left = [len(groups['virgin']) for catid, groups in data_state.iteritems() if catid not in cats_accomplished_success]
# two ways of seeing this:
# - consider only classes that have not accomplished goal, but might do it, based on our expectations (not sustainable)
# - consider ALL classes that have not accomplished goal. thinking big, this is the way (we have one year of new data)
# lets annotate them all, and it will me useful for the future: they are closer to the goal.


print("\n# how many gtless annotations do we have (ie voted but not gt yet)"
      "(in the classes that have NOT reached the target): %d" % sum(nb_sounds_gtless_left))
print("# how many virgin annotations do we have "
      "(in the classes that have NOT reached the target): %d" % sum(nb_sounds_virgin_left))


# ===================let us compute a budget estimation
# ===================let us compute a budget estimation
# ===================let us compute a budget estimation
# ===================let us compute a budget estimation

count_votes_gtless = 0
count_votes_virgin = 0
count_votes_needed_quantified = 0
data_needed = {}
data_noQE = {}
nb_sessions_needed = []
names_all_cats_needed = []
idx_tmp = 0

for catid, groups in data_state.iteritems():
    if catid not in cats_accomplished_success:
        # there are few classes with no QE, and it was set to 0.
        # This classes are strange and probably not worth going into
        if data_votes[catid]['QE'] > 0:

            # we want a target per category: this is the number of samples that we need per class
            data_needed[catid] = {}
            data_needed[catid]['name'] = data_onto_by_id[catid]['name']
            data_needed[catid]['gtneeded'] = TARGET_SAMPLES - (len(groups['PPgt']) + len(groups['PNPgt']))
            names_all_cats_needed.append(data_needed[catid]['name'])

            # debug
            # # if data_needed[catid]['name'] == 'String section':
            # if data_needed[catid]['name'] == 'Bathtub (filling or washing)':
            #     r = 4
            # # debug
            # if idx_tmp == 8:
            #     r = 4
            #     # print(data_onto_by_id[catid]['name'])

            # how many gt sounds can we get with the current gtless?
            # nb_gtless * QE
            data_needed[catid]['gt_from_gtless'] = np.floor(len(groups['gtless']) * data_votes[catid]['QE'])
            diff_gt = data_needed[catid]['gtneeded'] - data_needed[catid]['gt_from_gtless']

            if diff_gt > 0:
                # we need to use them all. This means voting ALL of them, the good and the bad ones
                # (and, additionally, we need diff_gt taken from virgin samples)
                # how many votes do we need for this? they require only partial agreement, since they have votes already
                data_needed[catid]['votes_for_gtless'] = len(groups['gtless']) * FACTOR_AGREE_GTLESS * FACTOR_FLEX
                data_needed[catid]['success'] = False

            else:
                # diff_gt < 0
                # we reach TARGET_SAMPLES only with gtless. WE dont even need all of them (only enough to reach TARGET)
                # how many votes do we need for this? they require only partial agreement, since they have votes already
                data_needed[catid]['votes_for_gtless'] = \
                    (len(groups['gtless']) + np.floor(diff_gt / data_votes[catid]['QE'])) * FACTOR_AGREE_GTLESS * FACTOR_FLEX
                data_needed[catid]['success'] = True

            # so far this is what I can do with the gtless. Now leverage virgin samples

            if diff_gt > 0:
                # now diff_gt is the target that we need to fill the class
                # the annotations that we need to get from the virgin subset
                # diff_gt / QE * FACTOR_FLEX
                data_needed[catid]['annot_needed_from_virgin'] = diff_gt/float(data_votes[catid]['QE']) * FACTOR_FLEX

                # do we have it?
                excess = len(groups['virgin']) - data_needed[catid]['annot_needed_from_virgin']
                if excess >= 0:
                    # yes, how many votes would that imply
                    # how many votes do we need for this? they require full agreement, since they are blank
                    data_needed[catid]['votes_for_virgin'] = data_needed[catid]['annot_needed_from_virgin'] * FACTOR_AGREE_VIRGIN
                    data_needed[catid]['success'] = True

                else:
                    # no, there are not enough, but we still annotate them all for the future,
                    # we may hide the category for now, but in the future this will be very helpful
                    data_needed[catid]['votes_for_virgin'] = len(groups['virgin']) * FACTOR_AGREE_VIRGIN
                    data_needed[catid]['success'] = False
            else:
                data_needed[catid]['votes_for_virgin'] = 0


            # nb of votes needed to reach TARGET_SAMPLES in the catid (or to run out of sounds)
            data_needed[catid]['votes_needed'] = data_needed[catid]['votes_for_gtless'] + data_needed[catid]['votes_for_virgin']

            # number of complete sessions to achieve it (ceiling)
            data_needed[catid]['sessions_needed'] = np.ceil(data_needed[catid]['votes_needed'] / float(NB_VOTES_PER_SESSION))
            # quantify this in number of sessions:
            # if we need 2.6 sessions, the subject will do 3, and we'll pay 3
            # KEY not sure the following comment is correct
            # but if we have enough data for 1.3 sessions (while we need 3), we'll be considering more money than needed
            nb_sessions_needed.append(data_needed[catid]['sessions_needed'])

            # recompute nb of votes with the number of sessions needed
            data_needed[catid]['votes_needed_quantified'] = data_needed[catid]['sessions_needed'] * NB_VOTES_PER_SESSION

            # global counters
            count_votes_virgin += data_needed[catid]['votes_for_virgin']
            count_votes_gtless += data_needed[catid]['votes_for_gtless']
            count_votes_needed_quantified += data_needed[catid]['votes_needed_quantified']

        else:
            data_noQE[catid] = {}

        # idx_tmp += 1 # for debug

# =======================
# we could print first the annotations that lead to number of votes
print("\n# Total amount of gtless votes needed (in classes that have NOT reached the target): %d" % count_votes_gtless)
print("# Total amount of virgin votes needed (in classes that have NOT reached the target): %d" % count_votes_virgin)

# 10 categories are 660 useful votes. This can be done in one day easily, with rests, carefully, FAQ n FS, 5 hours, 25E
price_gtless = count_votes_gtless / NB_VOTES_PACK_PERSON * PRICE_PACK_PERSON
price_virgin = count_votes_virgin / NB_VOTES_PACK_PERSON * PRICE_PACK_PERSON

print("\n# Money to gather gtless votes (in the classes that have NOT reached the target): %d euros" % price_gtless)
print("# Money to gather virgin votes (in the classes that have NOT reached the target): %d euros" % price_virgin)


# ==================================
print("\n\n# Total amount of sessions needed to FSD1.0 (in classes that have NOT reached the target):"
      " %d" % sum(nb_sessions_needed))
print("# Total amount of votes needed to FSD1.0 after quantification (in the classes that have NOT reached the target):"
      " %d" % count_votes_needed_quantified)

price_after_quantification = count_votes_needed_quantified / NB_VOTES_PACK_PERSON * PRICE_PACK_PERSON
print("# Money to gather all the votes needed to FSD1.0 after quantification "
      "(in the classes that have NOT reached the target): %d euros" % price_after_quantification)


catids_no_sucess = [catid for catid in data_needed if data_needed[catid]['success'] is False]
print("\n# After this, we still have classes that have not reached TARGET_SAMPLES, "
      "but all their content is annotated, hence easily expandable: %d" % len(catids_no_sucess))
print("# And categories that never had QE hence out of simulation: %d" % len(data_noQE))


# ==================================
# plot nb of sessions needed
idx_nb_sessions = np.argsort(-np.array(nb_sessions_needed))
nb_sessions_needed_sorted = list(nb_sessions_needed[val] for val in idx_nb_sessions)

# names_all_cats_needed = [data_onto_by_id[catid]['name'] for catid, sounds in data_needed.iteritems()]
names_all_cats_needed_sorted = list(names_all_cats_needed[val] for val in idx_nb_sessions)

# y_label = '# of sessions'
# fig_title = 'number of sessions needed per category to reach FSD1.0'
# plot_barplot(nb_sessions_needed_sorted,
#              names_all_cats_needed_sorted,
#              y_label,
#              fig_title,
#              18,
#              threshold=4)
#

# como es posible que en algunas categorias hagan falta 30 sessiones?
# -horrible QE
# -few gt currently
# -a lot of data available, (hence it is theoretically possible to achieve TARGET_SAMPLES)
# -ojo, igual matas dos pajaros. Mejoras los tag matching, re run del mapping, y ahorras pasta y tiempo
# a nadie le interesa tener un tio anotando cosas que sabes que estan mal. es tiempo y dinero.

print("\n\n# Total amount of SESSIONS needed to FSD1.0"
      " (in the classes that have NOT reached the target): %d" % sum(nb_sessions_needed))
print("# Based on that: Total amount of PACKS (ie groups of 10 sessions each):"
      " %d" % np.ceil(sum(nb_sessions_needed)/NB_SESSIONS_PER_PACK))
print("# Assuming %f packs per week by a subject, total amount of weeks:"
      " %d" % (NB_PACKS_PER_WEEK, np.ceil(sum(nb_sessions_needed)/NB_SESSIONS_PER_PACK)/NB_PACKS_PER_WEEK))
print("# Assuming %f subjects simultaneously, total amount of weeks in parallel:"
      " %d" % (NB_SUBJECTS_AVAILABLE, (np.ceil(sum(nb_sessions_needed)/NB_SESSIONS_PER_PACK)/NB_PACKS_PER_WEEK)/NB_SUBJECTS_AVAILABLE))


# ==============
full_paths = []
# print all cats sorted by nb of sessions
for i, j in zip(names_all_cats_needed_sorted, nb_sessions_needed_sorted):
    # print(i,j)
    print hierarchy_dict[data_onto_by_name[str(i)]['id']], '///', j

    hierarchy_paths_list = [str(item) for item in hierarchy_dict[data_onto_by_name[str(i)]['id']][0]]

    # concatenate all hiearchy path names with a > to allow alphabetical sorting
    full_path = ' > '.join(hierarchy_paths_list)
    full_paths.append(full_path)

# full_paths are the string paths for every class, in a list sorted by the number of sessions required.

# ===============
# now we wanna sort them by alphabetical order and apply that sorting to the number of sessions needed, to create groups
idx_alfa = sorted(range(len(full_paths)), key=lambda k: full_paths[k])

# sort by alfabetical order
full_paths_sorted_alfa = [full_paths[val] for val in idx_alfa]
nb_sessions_needed_sorted_alfa = [nb_sessions_needed_sorted[val] for val in idx_alfa]

# print
print('\n Printing by alphabetical order')
for i, j in zip(full_paths_sorted_alfa, nb_sessions_needed_sorted_alfa):
    print i, '///', j


a = 9



# TODO
# how do we deal with the hierarchy? annotations are unpopulated already
# doing the analysis of only the leafs omits certain sensible classes.
# cough instead of throat clearing
# thunderstorm instead of thunder
# do we prefer cat or meow? dog or bark?

# Discussion:
# the stats on landing page (98/396) use population, ie if bark reaches 100, we set as valid category, dog, domestic animal,
# and animal
# the horizontal bar per class in the platform presents the same: Bird has 397, out of which 217 are populated from children
# and 180 belong only to Bird
# in this script we do not populate. we treat classes as independent, hence here Bird has 180 valid GT.

# the most interesting case to annotate is the leafs, If we have data in leafs, the parents come naturally
# but there will be cases where we cannot have the leafs due to lack of data, but maybe a parent by mixing leafs.
# we could compute:
# find how many leafs cannot make it
# find how many leafs cannot make it but populate a succesful parent?


# if we were to use F8, what would be the data for it: how many virgin annotations do we have?
# - beginner classes
# - all classes
# how many samples are? and how many annotations? (a row is an annotation)

# if we were to use our pltaform, what would be the data for it:
# all the categories that have not reached the target
# both gtless and virgin
# how many samples are? and how many annotations?

# eval long sounds: how many are short and long?
# plan to re-run mapping

# how many classes can FSD1.0 have with(out) re-mapping?

# think on the data needed to eval: our platform vs F8

# left_
# -print QE on plots
# -sort by QE?


# =========================================================================================Settings plan A:
# mode = ALL_CATS. means meeting the target in 396 classes, independently, ie unpopulated. The most demanding case.
# Difference with LEAF mode:
# -coincides with the LEAF mode in 296 classes (75%)
# -with only the 296 leafs meeting the target (either TARGET_SAMPLES or less of) there is not enough,
# we'd be able to populate some of inmediate parents, but not all

# -so the difference in number of classes meeting TARGET_SAMPLES is not that high,
# but it includes some inmediate paretns (that are interesting)
# Using mode = ALL_CATS means we are demanding TARGET_SAMPLES in 25% more of the classes.
# But in some cases we actually need it cause children have little data
# Example: throat clearing has 30 gt. We need to annotate Cough almost entirely. with LEAF mode, we dont consider it.
# So in reality, we need a bit more than LEAF mode, but a bit less than ALL_CATS
# Lets use ALL_CATS for cost estimation, to be safe. Then we prioritize leafs and inmediate parents for annotation.
# nice thing: by using ALL_CATS, we make sure all cats have TARGET_SAMPLES,
# hence in the upper hierarchy levels, we can end up with several hundreds of samples.


# TARGET_SAMPLES = 130 to start with.
# Comparable with AudioSet.
# It means a bigger effort if we rely on good will, but if we paid for it, maybe it can be possible
# gives room for playing a bit when doing the splits.
# Else, we have to resign to split packs, hence dataset small and easy: useless.
# ideally, 150 would be better, but this may be too much for a target.
# Let's use 130, and if needed for some categories, we can annotate more in-house. if we have more subjects, we can increase to 150.

# Duration: 0.3 : 30. Too short are kind of useless.
# Too long are a mess and impact on dataset imbalance.
#

# NB_VOTES_PACK_PERSON = 660.0
# we can do packs of roughly 10 categories. it will depend on the siblings and coherence in the groups that can be made.
# 1 session of 1 class are 66 useful votes. 10 sessions are 660 votes.
# This can be done in 5 h easily, with rests, carefully, FAQ n FS, 25-30E. means one session + rest in 30 minutes
# of course this depends on the difficulty. Easier classes are faster and viceversa

# PRICE_PACK_PERSON = 25-30
# 5 hours of work at 6 euros/hour. This may be ok for UPF-people. But in Freesound we should give more?
#

# Finally, if needed we can always fix some classes in-house, if needed.
