
import json
import copy
import numpy as np
import matplotlib.pyplot as plt
from random import shuffle
import sys

"""
# the ultimate goal is:
 -to add more candidates to some categories that do not have a lot.
 -some have enough to reach 1k, but in others we have less than one hundred candidates in the dataset.
 -To mitigate the imbalance, we search for new candidates and then we add them only in the less abundant classes.

specifically, we do the dataset creation:
-load all the candidates (old, new) from where dev_LQ will be formed. And load dev_HQ and the eval (manually-verified portion, ie fixed fro FSDKaggle2018
-add data_dev_LQ_extended_800 (ie old candidates to dev_HQ)
-in classes that do not reach 800 samples, grab as needed from dev_LQ_new until reaching 1k (in most cases we will have to add them all, if we need to select, do random)

# create another dev_LQ_new_finally_included.json with *only* those that are added to complement data_dev_LQ_extended_800

"""


"""
LOAD section
"""


# FOLDER_DATA = 'kaggle3/'
FOLDER_DATA = '../kaggle3/'

MAX_TOTAL_SAMPLES_CLASS = 800          # max nb of samples in a class
MIN_RATIO_CAND_MV = 3                   # at least 80% are candidates

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


# load old candidates, before the addition of the new files from MArch2017.
# This is all the candidates that were in FSDKaggle2018 (when reaching 300 per class),
# plus more than were not included there (up to 1k per class, together with the HQ)
try:
    with open(FOLDER_DATA + 'json/new/data_dev_LQ_extended_800.json') as data_file:
        data_dev_LQ_extended_800 = json.load(data_file)
except:
    raise Exception('ADD A JSON with old candidates TO THE FOLDER ' + FOLDER_DATA + 'json/new/')


# load new candidates, from the inclusion of the new files from March2017 to July2018.
# This are totally new to FSDKaggle2018
# BEWARE: these are all that comply with the restrictions, but FF had some issues downloading them
# therefore out the 2.6k, only 1.9 can be used.
# we need to load the list of downloaded new candidates.
# TODO decide depending on Google (and if it actually helps)
try:
    # with open(FOLDER_DATA + 'json/new/data_dev_LQ_new.json') as data_file:
    with open(FOLDER_DATA + 'json/new/data_dev_LQ_new_allLicenses.json') as data_file:
        data_dev_LQ_new = json.load(data_file)
except:
    raise Exception('ADD A JSON with new candidates TO THE FOLDER ' + FOLDER_DATA + 'json/new/')


# load the list of downloaded new candidates
# try:
#     with open(FOLDER_DATA + 'json/new/data_dev_LQ_new_downloaded.json') as data_file:
#         data_dev_LQ_new_downloaded = json.load(data_file)
# except:
#     raise Exception('ADD A JSON with downloaded new candidates TO THE FOLDER ' + FOLDER_DATA + 'json/new/')

# load dev_HQ
try:
    with open(FOLDER_DATA + 'json/data_dev_HQ.json') as data_file:
        data_dev_HQ = json.load(data_file)
except:
    raise Exception('ADD A JSON with dev_HQ TO THE FOLDER ' + FOLDER_DATA + 'json/')

# load data_eval
try:
    with open(FOLDER_DATA + 'json/data_eval.json') as data_file:
        data_eval = json.load(data_file)
except:
    raise Exception('ADD A JSON with data_eval TO THE FOLDER ' + FOLDER_DATA + 'json/')


def check_nb_sounds_in_data_split(data_set, var_name):
    # sanity check: total number of sounds
    accum_fsids = []
    for catid, sounds in data_set.items():
        accum_fsids += sounds

    print('Number of sounds in %s: %d' % (var_name, len(set(accum_fsids))))
    print('Number of categories: %d' % len(data_dev_LQ_extended_800))
    return 0

def plot_barplot(data_bottom, data_up, x_labels, y_label, fig_title, legenda, MAX_VERT_AX, threshold=None):
    ind = np.arange(len(data_bottom))  # the x locations for the groups
    width = 0.6  # the width of the bars: can also be len(x) sequence
    axes = [-0.4, len(data_bottom), 0, MAX_VERT_AX]

    fig = plt.figure()
    ax = fig.add_subplot(111)
    p1 = plt.bar(ind, data_bottom, width=width, color='blue')
    p2 = plt.bar(ind, data_up, width=width, bottom=data_bottom, color='cyan')
    # horizontal line indicating the threshold
    if threshold:
        plt.plot([0, 48], [threshold, threshold], "k--", linewidth=3)
    plt.xticks(fontsize=8, rotation=90)
    plt.xticks(ind + width/2, x_labels)
    # plt.xticks(ind, x_labels)
    plt.yticks(fontsize=10)
    plt.ylabel(y_label, fontsize=11)
    # plt.title(fig_title)
    # plt.yticks(np.arange(0, 81, 10))
    plt.legend((p1[0], p2[0]), legenda, fontsize=9)
    plt.axis(axes)
    ax.yaxis.grid(True)
    # plt.grid(True)


    # size_w = 3.487
    size_w = 10
    # size_h = size_w / 1.618
    size_h = 6
    # golden_mean = (np.sqrt(5) - 1.0) / 2.0  # Aesthetic ratio
    # size_h = size_w * golden_mean  # height in inches

    size_w = 12
    # size_h = size_w / 1.618
    size_h = 7

    fig.set_size_inches(size_w, size_h)

    plt.show()
    # fig.savefig('plot.png')


def do_figure_barplot(data_dev_out):
    # -- # bar plot of number of HQ/LQ for every category for DEVELOPMENT set----

    names_all_cats_dev = [data_onto_by_id[cat_id]['name'] for cat_id, v in data_dev_out.items()]
    nb_HQ_per_cat_dev = [len(v['mv']) for cat_id, v in data_dev_out.items()]
    nb_LQ_per_cat_dev = [len(v['cand']) for cat_id, v in data_dev_out.items()]

    # old
    # nb_sounds_per_cat_dev = [len(v['all']) for cat_id, v in data_dev_out.items()]
    # are dicts read in the same order? it seems ok
    # subtracting element wise in lists
    # nb_LQ_per_cat_dev = [i - j for i, j in zip(nb_sounds_per_cat_dev, nb_HQ_per_cat_dev)]

    y_label = '# of audio samples'
    fig_title = 'number of samples per category in DEV, split in HQ - LQ'
    legenda = ('manually-verified', 'non-verified')

    # alphabeticaly
    idx_alpha = sorted(range(len(names_all_cats_dev)), key=lambda k: names_all_cats_dev[k])
    names_all_cats_dev_idx_alpha = list(names_all_cats_dev[val] for val in idx_alpha)
    nb_HQ_per_cat_dev_idx_alpha = list(nb_HQ_per_cat_dev[val] for val in idx_alpha)
    nb_LQ_per_cat_dev_idx_alpha = list(nb_LQ_per_cat_dev[val] for val in idx_alpha)

    plot_barplot(nb_HQ_per_cat_dev_idx_alpha,
                 nb_LQ_per_cat_dev_idx_alpha,
                 names_all_cats_dev_idx_alpha,
                 y_label,
                 fig_title,
                 legenda,
                 1200,
                 threshold=300)

"""
report numbers to check all is good
"""

check_nb_sounds_in_data_split(data_dev_LQ_extended_800, 'data_dev_LQ_extended_800')
check_nb_sounds_in_data_split(data_dev_LQ_new, 'data_dev_LQ_new')
check_nb_sounds_in_data_split(data_dev_HQ, 'data_dev_HQ')
check_nb_sounds_in_data_split(data_eval, 'data_eval')
# all is good

# ==================create eval set
# the same as in FSDKaggle2018.
data_eval_out = copy.deepcopy(data_eval)


# ==================create dev set
# add HQ aka mV portion
# instead of deepcopying, lets create a more complex structure to have more info
# data_dev_out = copy.deepcopy(data_dev_HQ)
data_dev_out = {key: {'all': [], 'mv': [], 'cand':[]} for key in data_dev_HQ}
for cat_id, v in data_dev_out.items():
    data_dev_out[cat_id]['all'] += data_dev_HQ[cat_id]
    data_dev_out[cat_id]['mv'] += data_dev_HQ[cat_id]


# add old candidates
for cat_id, v in data_dev_out.items():
    data_dev_out[cat_id]['all'] += data_dev_LQ_extended_800[cat_id]
    data_dev_out[cat_id]['cand'] += data_dev_LQ_extended_800[cat_id]

# -- # bar plot of number of HQ/LQ for every category for DEVELOPMENT set----
do_figure_barplot(data_dev_out)


# for the classes with less than MAX_TOTAL_SAMPLES_CLASS, add new candidates, up to MAX_TOTAL_SAMPLES_CLASS
# TODO need to check who are available???? FF
for cat_id, v in data_dev_out.items():
    if len(data_dev_out[cat_id]['all']) < MAX_TOTAL_SAMPLES_CLASS:

        # we need up to MAX_TOTAL_SAMPLES_CLASS
        nb_needed = MAX_TOTAL_SAMPLES_CLASS - len(data_dev_out[cat_id]['all'])
        shuffle(data_dev_LQ_new[cat_id])
        data_dev_out[cat_id]['all'] += data_dev_LQ_new[cat_id][:nb_needed]
        data_dev_out[cat_id]['cand'] += data_dev_LQ_new[cat_id][:nb_needed]

# -- # bar plot of number of HQ/LQ for every category for DEVELOPMENT set----
do_figure_barplot(data_dev_out)
# tampoco se gana tanto con esto.... es poquito


# at this point I have added all the candidates that I had.
# apply filter noisy data: keep clases with ratio X:1 = X00:100
data_dev_out_ratio = {}
for cat_id, v in data_dev_out.items():
    ratio = len(v['cand']) / float(len(v['mv']))
    data_dev_out[cat_id]['ratio'] = ratio

    if ratio >= MIN_RATIO_CAND_MV:
        data_dev_out_ratio[cat_id] = {}
        data_dev_out_ratio[cat_id] = data_dev_out[cat_id]

# -- # bar plot of number of HQ/LQ for every category for DEVELOPMENT set----
do_figure_barplot(data_dev_out_ratio)


# sanity checks: HQ and LQ disjoint, lo mismo con dev y eval. and no duplicates
for cat_id, v in data_dev_out_ratio.items():
    # sanity check: there should be no duplicated fsids within the groups of annotations
    if (len(v['all']) != len(set(v['all'])) or len(v['cand']) != len(set(v['cand'])) or
                len(v['mv']) != len(set(v['mv']))):
        print(data_onto_by_id[cat_id]['name'], cat_id)
        sys.exit('duplicates in the groups of annotations of the printed category')

    # sanity check: dev_LQ must be disjoint with all other groups: dev_HQ and dev_eval
    if (list(set(v['cand']) & set(v['mv'])) or list(set(v['cand']) & set(data_eval_out[cat_id])) or
            list(set(v['mv']) & set(data_eval_out[cat_id]))):
        print(data_onto_by_id[cat_id]['name'], cat_id)
        sys.exit('not disjoint groups in the printed category')

"""
report for paper
"""
# create csvs al estilo Kaggle
# id, mv, class, algo mas? esto esta en script de kaggle? pandas? ver pandas en main de KAggle.


# mola tener a mano los json que usaste, para el futuro:
# data_dev_LQ_extended_800
# dev_LQ_new_finally_included.json (segun lo que baje FF y lo que meta yo hasta 800 TODO
# data_dev_HQ
# data_eval
# create another dev_LQ_new_finally_included.json with *only* those that are added to complement data_dev_LQ_extended_800


# report main stats
for idx, (cat_id, v) in enumerate(data_dev_out_ratio.items(), 1):
    print("%d - %-25s: all: %-3d, mv: %-3d, cand: %-3d" % (idx, data_onto_by_id[cat_id]['name'], len(v['all']), len(v['mv']), len(v['cand'])))
# habria que reportar algo mas igual


a=9




"""
# hay pocas clases con muchos candidates, como 12. pense que serian mas.
# possible actions:
# A-incluir NC y sampling+ en los new candidates es straightforward. todos son candidates y saldran algunos mas.
cuanto gano con esto? igual nada...
DONE, no cambia mucho...

# B-incluir NC y sampling+ en los old candidates
# (ojo, esto igual es algo mas de lio.. porque el filtro esta arriba del procedure,
# modificarlo cambiaria el numero de samples per class (both HQ y LQ)
# yo quiero mantener la HQ y simplemente tener mas candidates, asi que habria de ser como post-processing stage
# seria coger para cada clase, todos los que son candidates, never voted y los que tienen esas licencias, y meterlos
igual esto es algo lio para ganar un 15% de audios en esas clases... al final salen 1 o 2 clases... igual paso.
PASO, cambia poco

# C-limitar el maximo a 800 para que el imbalance se note menos.
DONE

# resultado de esto es simplemente cambiar los json arriba. nada mas.

el problema es dealing with noisy labels: SSL to turn them, or measures for robustness against them
para ello necesitas un dataset que tenga noisy labels, y una small par of mV labels
need clases que cumplan esto.
new filter: ratio 4:1 = 400:100, ie un 20% como mucho de mV, ie como minimo 80% de noisy labels.
new filter: ratio 3:1 = 300:100, ie un 25% como mucho de mV, ie como minimo 75% de noisy labels. no esta mal.
DONE

"""


