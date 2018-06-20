import sys
import json
import numpy as np
import copy
import matplotlib.pyplot as plt



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
# nice to compute this class-dependent
FACTOR_AGREE_GTLESS = 1.5
FACTOR_AGREE_VIRGIN = 2.6
FACTOR_FLEX = 1.1

mode = 'ALL_CATS'
# mode = 'BEGINNER'
# mode = 'ADVANCED'
# mode = 'VALID_LEAF'

MINLEN = 0.3  # duration
MAXLEN = 30.0
FOLDER_DATA = 'kaggle3/'
MIN_VOTES_CAT = 70  # minimum number of votes per category to produce a QE.
TARGET_SAMPLES = 100

"""load initial data with votes, clip duration and ontology--------------------------------- """

# this the result of the mapping from FS sounds to ASO.
# 268k sounds with basic metadata and their corresponding ASO id.
# useful to get the duration of every sound
try:
    with open(FOLDER_DATA + 'json/FS_sounds_ASO_postIQA.json') as data_file:
        data_mapping = json.load(data_file)
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


try:
    # from March1, in the dumps we include only the trustable votes  (verification clips are met)
    # with open(FOLDER_DATA + 'json/votes_dumped_2018_May_16.json') as data_file:
    with open(FOLDER_DATA + 'json/votes_dumped_2018_Jun_18.json') as data_file:
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
            if (data_mapping[str(fsid)]['duration'] < _maxlen) and (data_mapping[str(fsid)]['duration'] >= _minlen):
                data_out[catid]['PP'].append(fsid)

        for fsid in votes['PNP']:
            if (data_mapping[str(fsid)]['duration'] < _maxlen) and (data_mapping[str(fsid)]['duration'] >= _minlen):
                data_out[catid]['PNP'].append(fsid)

        for fsid in votes['NP']:
            if (data_mapping[str(fsid)]['duration'] < _maxlen) and (data_mapping[str(fsid)]['duration'] >= _minlen):
                data_out[catid]['NP'].append(fsid)

        for fsid in votes['U']:
            if (data_mapping[str(fsid)]['duration'] < _maxlen) and (data_mapping[str(fsid)]['duration'] >= _minlen):
                data_out[catid]['U'].append(fsid)

        for fsid in votes['candidates']:
            if (data_mapping[str(fsid)]['duration'] < _maxlen) and (data_mapping[str(fsid)]['duration'] >= _minlen):
                data_out[catid]['candidates'].append(fsid)

    return data_out


def check_gt_v2(_group, _fsid, _catid, _votes, _fsids_assigned_cat, _data):
    """ # check if fsid has GT within a given group (PP,PNP,NP,U) of a category given by catid
    # if it does, add it to assigned fsids and send it to the corresponding group in data
    """
    assigned = False
    if _votes[_group].count(_fsid) > 1:
        if _fsid not in _fsids_assigned_cat:
            _data[_catid][_group + 'gt'].append(_fsid)
            _fsids_assigned_cat.append(_fsid)
            assigned = True
    return _data, _fsids_assigned_cat, assigned


def plot_barplot_grouped2(data_left, data_right, x_labels, y_label, fig_title, legenda, MAX_VERT_AX, threshold=None):
    ind = np.arange(len(data_left))  # the x locations for the LEFT bars
    width = 0.35  # the width of the bars: can also be len(x) sequence
    axes = [-0.5, len(data_left), 0, MAX_VERT_AX]

    fig, ax = plt.subplots()
    # fig = plt.figure()
    # ax = fig.add_subplot(111)
    p1 = ax.bar(ind, data_left, width=width, color='blue')
    p2 = ax.bar(ind + width, data_right, width=width, color='cyan')
    # horizontal line indicating the threshold
    if threshold:
        plt.plot([0, 48], [threshold, threshold], "k--", linewidth=3)
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
    p1 = ax.bar(ind, data_left, width=width, color='blue')
    p2 = ax.bar(ind + width, data_middle, width=width, color='cyan')
    p3 = ax.bar(ind + 2*width, data_right, width=width, color='green')
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
*****************************************************************************SCRIPT
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

# apply FILTER 0 and 1: by taking the union of the above
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
# including NC-license for now

data_votes_study = data_votes_all
""" # Categorize the annotations/sounds in every category: valid GT, nonGT, virgin***********************************"""
"""******************************************************************************************************************"""

# considering only sounds between  [MINLEN: MAXLEN): data_votes_study

# create data_stats_l_mid with keys with catids and empty dicts as values
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
    if data_onto_by_id[catid]['name'] == 'Pizzicato':
        a=8

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


# sort classes according to several criteria for plotting
# sort in descending order of valid samples
idx_valid = np.argsort(-np.array(nb_sounds_valid))
# sort in descending order of gtless samples; since they have a lot pending in the platform, this could be ok to stay in platform
idx_gtless = np.argsort(-np.array(nb_sounds_gtless))
# sort in descending order of virgin samples, this could be ok for F8
idx_virgin = np.argsort(-np.array(nb_sounds_virgin))

y_label = '# of audio samples'
# fig_title = 'number of samples per category'
# legenda = ('valid', 'virgin')
# plot_barplot_grouped2(nb_sounds_valid_sorted,
#                      nb_sounds_virgin_sorted,
#                      names_all_cats_sorted,
#                      y_label,
#                      fig_title,
#                      legenda,
#                      400)

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
                          threshold=100)

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
                          threshold=100)

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
                          threshold=100)



""" # print report***************************************************************************************************"""
"""******************************************************************************************************************"""

print("**************************************************Report for mode %s" % mode)


cats_accomplished_success = {}
cats_estimated_success = {}
for catid, groups in data_state.iteritems():
    if len(groups['PPgt']) + len(groups['PNPgt']) >= TARGET_SAMPLES:
        cats_accomplished_success[catid] = len(groups['PPgt']) + len(groups['PNPgt'])

    else:
        estimated_gt = len(groups['PPgt']) + len(groups['PNPgt']) + (len(groups['gtless']) + len(groups['virgin']))* data_votes[catid]['QE']
        if estimated_gt>= TARGET_SAMPLES:
            cats_estimated_success[catid] = estimated_gt

print("# how many cats have already TARGET_SAMPLES samples? (beware, unpopulated): %d" % len(cats_accomplished_success))
print("# how many cats can reach TARGET_SAMPLES with gtless and virgin, considering QE (including already accomplished): %d" % (len(cats_estimated_success) + len(cats_accomplished_success)))


print("\n# how many virgin annotations do we have: %d" % sum(nb_sounds_virgin))
print("# how many gtless annotations do we have (ie voted but not gt yet): %d" % sum(nb_sounds_gtless))

nb_sounds_gtless_left = [len(groups['gtless']) for catid, groups in data_state.iteritems() if catid not in cats_accomplished_success]
nb_sounds_virgin_left = [len(groups['virgin']) for catid, groups in data_state.iteritems() if catid not in cats_accomplished_success]
# two ways of seeing this:
# - consider ALL categories that have not accomplished goal. thinking big, this is the way (we have one year of new data)
# - consider the categories that have not accomplished goal, but might do it, based on our expectations

print("\n# how many virgin annotations do we have (in the classes that have NOT reached the target): %d" % sum(nb_sounds_virgin_left))
print("# how many gtless annotations do we have (ie voted but not gt yet)(in the classes that have NOT reached the target): %d" % sum(nb_sounds_gtless_left))


count_votes_gtless = 0
count_votes_virgin = 0
data_needed = {}
data_noQE = {}
for catid, groups in data_state.iteritems():
    if catid not in cats_accomplished_success:
        # there are afew categories that have no QE, and it was set to 0. This classes are strange and probably not worth going into
        if data_votes[catid]['QE'] > 0:
            # we want a target per category: this is the number of samples that we need per class
            data_needed[catid] = {}
            data_needed[catid]['gtneeded'] = TARGET_SAMPLES - (len(groups['PPgt']) + len(groups['PNPgt']))

            # how many annotations can we get with the current gtless?
            # nb_gtless * QE
            data_needed[catid]['gt_from_gtless'] = np.floor(len(groups['gtless']) * data_votes[catid]['QE'])
            diff_gt = data_needed[catid]['gtneeded'] - data_needed[catid]['gt_from_gtless']

            if diff_gt > 0:
                # we need to use them all. This means voting them ALL of them, the good and the bad ones
                # and, additionally, we need diff gt taken from virgin samples
                # how many votes do we need for this? they require only partial agreement, since they have votes already
                data_needed[catid]['votes_for_gtless'] = len(groups['gtless']) * FACTOR_AGREE_GTLESS * FACTOR_FLEX
                data_needed[catid]['success'] = False

            else:
                # we reach TARGET_SAMPLES only with gtless. WE dont even need all of them (only enough to reach TARGET)
                # how many votes do we need for this? they require only partial agreement, since they have votes already
                data_needed[catid]['votes_for_gtless'] = (len(groups['gtless']) + np.floor(diff_gt / data_votes[catid]['QE'])) * FACTOR_AGREE_GTLESS * FACTOR_FLEX
                data_needed[catid]['success'] = True

            # so far this is what I can do with the gtless. Now leverage virgin samples

            if diff_gt > 0:
                # now diff_gt is the target that we need to fill the class
                # the annotations that we need to get from te virgin subset
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
                    # no, there are not enough, so use them all and still we need more, or hide the category for now
                    data_needed[catid]['votes_for_virgin'] = len(groups['virgin']) * FACTOR_AGREE_VIRGIN
                    data_needed[catid]['success'] = False
            else:
                data_needed[catid]['votes_for_virgin'] = 0

            count_votes_virgin += data_needed[catid]['votes_for_virgin'] if data_needed[catid]['votes_for_virgin'] else 0
            count_votes_gtless += data_needed[catid]['votes_for_gtless']

        else:
            data_noQE[catid] = {}

# we could print first the annotations that lead to number of votes
print("# Total amount of gtless votes needed (in the classes that have NOT reached the target): %d" % count_votes_gtless)
print("# Total amount of virgin votes needed (in the classes that have NOT reached the target): %d" % count_votes_virgin)

# 10 categories are 660 useful votes. This can be done in one day easily, with rests, carefully, FAQ n FS, 5 hours, 25E

price_gtless = count_votes_gtless / 660.0 * 25
price_virgin = count_votes_virgin / 660.0 * 25
print("# Money to gather gtless votes (in the classes that have NOT reached the target): %d euros" % price_gtless)
print("# Money to gather virgin votes (in the classes that have NOT reached the target): %d euros" % price_virgin)

catids_no_sucess = [catid for catid in data_needed if data_needed[catid]['success']==False]
print("\n# After this, we still have categories that have not reached the target: %d" % len(catids_no_sucess))
print("\n# And categories that never had QE hence out of simulation: %d" % len(data_noQE))


a=9
# to consider, we have blocks of 66 annotations to be validated. That is our mininimum presentation unit.


# TODO
# how do we deal with the hierarchy? annotations are unpopulated already
# doing the analysis of only the leafs omits certain sensible classes.
# cough instead of throat clearing
# thunderstorm instead of thunder
# do we prefer cat or meow? dog or bark?

# Discussion:
# the stats on landing page (98/396) use population, ie if bark reaches 100, we set as valid category, dog, domestic animal, and animal, correct?
# the horizontal bar per class in the platform presents the same: Bird has 397, out of which 217 are populated from children and 180 belong only to Bird
# in this script we do not populate. we treat classes as independent, hence here Bird has 180 valid GT.

# the most interesting case to annotate is the leafs, If we have data in leafs, the parents come naturally
# but there will be cases where we cannot have the leafs due to lack of data, but maybe a parent by mixing leafs.
# we could compute:
# find how many leafs cannot make it
# find how many leafs cannot make it but populate a succesful parent?


# ask specific questions:
# how many cats have already 100 samples? does it match the platform?
# -here we dont populate so difficult to say


# how many cats can reach 100 with what we have, considering:
# -gtless + QE
# -virgin + QE
# see doc
# this question is pertinent for the leafs

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
#