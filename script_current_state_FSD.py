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


MINLEN = 0.3  # duration
MAXLEN = 30.0
FOLDER_DATA = 'kaggle3/'
MIN_VOTES_CAT = 70  # minimum number of votes per category to produce a QE.


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
    with open(FOLDER_DATA + 'json/votes_dumped_2018_May_16.json') as data_file:
        data_votes_raw = json.load(data_file)
except:
    raise Exception('ADD A DUMP JSON FILE OF THE FSD VOTES TO THE FOLDER ' + FOLDER_DATA + 'json/')

# data_votes_raw is a dict where every key is a cat
# the value of every cat is a dict, that contains 5 keys: PP, PNP, NP, U, candidates
# the corresponding values are a list of Freesound ids
#
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


def plot_barplot_grouped(data_left, data_right, x_labels, y_label, fig_title, legenda, MAX_VERT_AX, threshold=None):
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


"""
*****************************************************************************SCRIPT
"""


""" # remove unwanted sounds from specific categories before doing anything else*************************************"""
"""******************************************************************************************************************"""

# sanity check: total number of mapped sounds?
accum_fsids = []
for catid, votes in data_votes_raw.iteritems():
    # accum_fsids.append(votes['candidates'])
    accum_fsids += votes['candidates']

print('Number of sounds in the dump: %d' % len(set(accum_fsids)))

# First off, we may need to do some pre-processing to remove some sounds we already now they are wron
# # remove the sounds from data_votes_raw
data_votes = copy.deepcopy(data_votes_raw)

# empty for now


""" # report on how many categories we have with at least one sample*************************************"""
"""******************************************************************************************************************"""

print('Number of categories from the dump: %d' % len(data_votes))

# lets compute the QE here, considering all the sounds
# for every category compute QE here number of votes len(PP) + len(PNP) / all
# QE should only be computed if there are more than MIN_VOTES_CAT votes. else not reliable, and hence defined to 0
for catid, votes in data_votes.iteritems():
    if (len(votes['PP']) + len(votes['PNP']) + len(votes['NP']) + len(votes['U'])) >= MIN_VOTES_CAT:
        data_votes[catid]['QE'] = (len(votes['PP']) + len(votes['PNP'])) / float(
            len(votes['PP']) + len(votes['PNP']) + len(votes['NP']) + len(votes['U']))

    else:
        data_votes[catid]['QE'] = 0

# hence we keep the QE just in case

""" # apply initial constraints for the study*************************************"""
"""******************************************************************************************************************"""

# FILTERS TO APPLY FOR SIMPLICITY
# 1-lets focus on the leaf categories for now (simplest case)
# 2-split into short, mid and long sounds. Focus on mid

# FILTER 1: Consider only leaf categories: 474 out of the initial 632
# for o in data_votes. o = catid
# create a dict of dicts. The latter are key=o, and value the actual value (data_votes[o])
data_votes_l = {o: data_votes[o] for o in data_votes if len(data_onto_by_id[o]['child_ids']) < 1}
print 'Number of leaf categories in the dump: ' + str(len(data_votes_l))

# FILTER 2: Apply duration filter: Within the 474 categories:
# short sounds [0:MINLEN)
# mid sounds [MINLEN: MAXLEN)
# long sounds [MAXLEN, inf)

# data_votes_l_mid = copy.deepcopy(data_votes_l)
data_votes_l_short = apply_duration_filter(data_votes_l, 0, MINLEN)
data_votes_l_mid = apply_duration_filter(data_votes_l, MINLEN, MAXLEN)
data_votes_l_long = apply_duration_filter(data_votes_l, MAXLEN, 95.0)
data_votes_l_all = data_votes_l
# including NC-license for now

# no more filters for now, we just want to know which data we have
# print()
# to carry out the study
data_votes_study = data_votes_l_mid
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

names_all_cats = [data_onto_by_id[cat_id]['name'] for cat_id, sounds in data_state.iteritems()]

nb_sounds_PPgt = [len(groups['PPgt']) for cat_id, groups in data_state.iteritems()]
nb_sounds_PNPgt = [len(groups['PNPgt']) for cat_id, groups in data_state.iteritems()]
nb_sounds_valid = [i + j for i, j in zip(nb_sounds_PPgt, nb_sounds_PNPgt)]

# do the set on data_state[catid]['gtless'] as we have added same ids several times!
nb_sounds_gtless = [len(set(groups['gtless'])) for cat_id, groups in data_state.iteritems()]
nb_sounds_virgin = [len(groups['virgin']) for cat_id, groups in data_state.iteritems()]

# sort in descending
idx_valid = np.argsort(-np.array(nb_sounds_valid))


y_label = '# of audio samples'
fig_title = 'number of samples per category'
legenda = ('valid', 'virgin')

#
# plot_barplot(nb_HQ_per_cat_dev,
#              nb_LQ_per_cat_dev,
#              names_all_cats_dev,
#              y_label,
#              fig_title,
#              legenda,
#              305)
#
# plot_barplot_grouped(nb_HQ_per_cat_dev,
#                      nb_LQ_per_cat_dev,
#                      names_all_cats_dev,
#                      y_label,
#                      fig_title,
#                      legenda,
#                      260)

# say we want the classes in development set ordered by median of clip duration (consider only dev set)
names_all_cats_sorted = list(names_all_cats[val] for val in idx_valid)
nb_sounds_valid_sorted = list(nb_sounds_valid[val] for val in idx_valid)
nb_sounds_gtless_sorted = list(nb_sounds_gtless[val] for val in idx_valid)
nb_sounds_virgin_sorted = list(nb_sounds_virgin[val] for val in idx_valid)


# plot_barplot(nb_HQ_per_cat_dev_sorted,
#              nb_LQ_per_cat_dev_sorted,
#              names_all_cats_dev_sorted,
#              y_label,
#              fig_title,
#              legenda,
#              305)

plot_barplot_grouped(nb_sounds_valid_sorted,
                     nb_sounds_virgin_sorted,
                     names_all_cats_sorted,
                     y_label,
                     fig_title,
                     legenda,
                     400)

# another option would be to group them by families, as in the excel
a=9


# TODO
# how to select the 396 'valid' classes. where is that info?, and select only the leafs within them
# how do we deal with the hierarchy?
# the stats on landing use population, right?, ie if bark reaches 100, we set as valid, dog, domestic animal, and animal
# and how about the horizontal bar per class?
# grab new dump and all durations and compare.

# plot 3 bars with the gtless, narrower bars, put some shadow every 50
# put the QE on top of the bars, to estimate the ratio of gtless and virgin visually.
# sort by virgin

# ask specific questions:
# how many cats have already 100 samples? does it match the platform?
# how many cats can reach 100 with what we have, considering:
# -gtless + QE
# -virgin + QE
# see doc

# if we were to use F8, what would be the data for it:
# - easy classes. do experi for them. grab ids from excel?
# - virgin candidates, for clarity
# how many samples are? and how many annotations?

# if we were to use our pltaform, what would be the data for it:
# all the categories that have not reached the target
# both gtless and virgin
# how many samples are? and how many annotations?

# eval long sounds: how many are short and long?
# plan to re-run mapping
