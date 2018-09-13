
import json
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
# import matplotlib
# matplotlib.get_backend()

# wm = plt.get_current_fig_manager()
# wm.window.attributes('-topmost', 1)
# wm.window.attributes('-topmost', 0)

"""
todo
rehacer estos plots, pero cargando datos desde
2018_Mar_14_FSDKaggle2018_delivered/dataset_dev.csv

y convirtiendo a formato tipico de json

lo hiciste ya en...

"""

FOLDER_DATA = ''
FLAG_PLOT = False

#### DEFINE CONSTANTS HERE ###


# this the result of the mapping from FS sounds to ASO.
# 268k sounds with basic metadata and their corresponding ASO id.
# useful to get the duration of every sound
try:
    with open(FOLDER_DATA + 'json/FS_sounds_ASO_postIQA.json') as data_file:
        data_duration = json.load(data_file)
except:
    raise Exception('CHOOSE A MAPPING FILE AND ADD IT TO ' + FOLDER_DATA +'json/ FOLDER (THE FILE INCLUDE DURATION INFORMATION NEEDED)')

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

#
#
# all_ids of the sounds that compose the dataset
with open(FOLDER_DATA + '2018_Mar_14_FSDKaggle2018_delivered/all_freesound_ids.json') as data_file:
    all_ids = json.load(data_file)

# only to grab 41 classes
with open(FOLDER_DATA + 'json/data_eval.json') as data_file:
    data_41classes = json.load(data_file)

# load dataset_dev.csv
try:
    train_csv_kaggle = pd.read_csv(FOLDER_DATA + '2018_Mar_14_FSDKaggle2018_delivered/dataset_dev.csv', header=None)
except:
    raise Exception('ADD A csv with dataset_dev TO THE FOLDER ' + FOLDER_DATA + '2018_Mar_14_FSDKaggle2018_delivered/')

# all_ids of the sounds that compose the DEVELOPMENT dataset
# from train_csv_kaggle to a dictionary with cat_ids as key and list of fs_ids as value
data_dev = {key: [] for key in data_41classes}
for index, row in train_csv_kaggle.iterrows():
    data_dev[row[1]].append(row[0])

# # all_ids of the manually verified sounds that compose the DEVELOPMENT dataset (useful for plotting HQ vs LQ)
# from train_csv_kaggle to a dictionary with cat_ids as key and list of fs_ids as value
data_dev_HQ = {key: [] for key in data_41classes}
for index, row in train_csv_kaggle.iterrows():
    # only if the sample is manually_verified (the candidates have already been loaded before in this script)
    if row[3] == 1:
        data_dev_HQ[row[1]].append(row[0])


# load dataset_eval
try:
    test_csv_kaggle = pd.read_csv(FOLDER_DATA + '2018_Mar_14_FSDKaggle2018_delivered/dataset_eval.csv', header=None)
except:
    raise Exception('ADD A csv with dataset_eval TO THE FOLDER ' + FOLDER_DATA + '2018_Mar_14_FSDKaggle2018_delivered/')

# from test_csv_kaggle to a dictionary with cat_ids as key and list of fs_ids as value
data_eval = {key: [] for key in data_41classes}
for index, row in test_csv_kaggle.iterrows():
    # print(index, row)
    data_eval[row[1]].append(row[0])



# filename = 'dataset_eval.csv'
# raw_data = open(filename, 'rt')
# data_eval = np.loadtxt(raw_data, delimiter=",")
# print(data_eval.shape)

# ===============================================================================================
# --------------------------------------functions for plotting---------------------------------
# turn interactive mode on

plt.ion()

def plot_histogram(x,bins,fig_title,axes):
    # plot histogram given an array x
    plt.figure()
    n, bins, patches = plt.hist(x, bins=bins, facecolor='blue', alpha=0.75, histtype='bar', ec='black')
    plt.xlabel('seconds')
    plt.ylabel('# of sounds')
    plt.title(fig_title)
    plt.axis(axes)
    plt.grid(True)
    # plt.pause(0.001)

    # trials to open figures in the back to avoid interrupting
    wm = plt.get_current_fig_manager()
    # wm.window.attributes('-topmost', 1)
    wm.window.attributes('-topmost', 0)
    # get_current_fig_manager().window.attributes('-topmost', 0)
    # fig = gcf()
    # fig.canvas.manager.window.attributes('-topmost', 0)
    # plt.show()


def plot_boxplot(data, x_labels, fig_title, y_label):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    # for tick in ax.get_xticklabels():
    #     tick.set_rotation(45)
    plt.xticks(fontsize=7, rotation=45)
    bp = ax.boxplot(data, patch_artist=True)
    ## change color and linewidth of the whiskers
    for whisker in bp['whiskers']:
        whisker.set(color='#7570b3', linewidth=1)

    for flier in bp['fliers']:
        flier.set(marker='.', color='#e7298a', alpha=0.5)

    ## change color and linewidth of the medians
    for median in bp['medians']:
        median.set(color='#ef0707', linewidth=3)

    axes = [0.5, len(data) + 0.5, 0, 30.5]
    plt.axis(axes)
    ax.set_xticklabels(x_labels)
    plt.ylabel(y_label)
    plt.title(fig_title)
    plt.grid(True)
    plt.show()
    # plt.pause(0.001)


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
    # size_w = 10
    # size_h = size_w / 1.618
    # size_h = 6
    # golden_mean = (np.sqrt(5) - 1.0) / 2.0  # Aesthetic ratio
    # size_h = size_w * golden_mean  # height in inches

    size_w = 12
    # size_h = size_w / 1.618
    size_h = 7

    fig.set_size_inches(size_w, size_h)

    plt.show()
    fig.savefig('plot.png')


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


def plot_barplot_simple(data, x_labels, y_label, fig_title, MAX_VERT_AX, threshold=None):
    ind = np.arange(len(data))  # the x locations for the LEFT bars
    width = 0.71  # the width of the bars: can also be len(x) sequence
    # axes = [-0.5, len(data), 0, MAX_VERT_AX]
    axes = [-0.5, len(data), 0.65, MAX_VERT_AX]

    fig, ax = plt.subplots()
    # fig = plt.figure()
    # ax = fig.add_subplot(111)
    # p1 = ax.bar(ind, data, width=width, color='blue')
    p1 = ax.bar(ind, data, width=width, color='#ffd28c')

    # horizontal line indicating the threshold
    if threshold:
        plt.plot([0, 48], [threshold, threshold], "k--", linewidth=3)

    # magic to plot the labels correctly pointing in parallel to a bar point
    xticks_pos = [0.5 * patch.get_width() + patch.get_xy()[0] for patch in p1]
    plt.xticks(xticks_pos, x_labels, ha='right', rotation=45, fontsize=13)

    # plt.xticks(ind + width/2, x_labels, fontsize=13)
    # plt.xticks(ind, x_labels, fontsize=13, rotation=45)
    plt.yticks(fontsize=13)
    plt.ylabel(y_label, fontsize=16)    # ax.set_title(fig_title)
    # plt.yticks(np.arange(0, 81, 10))
    # plt.title(fig_title)
    plt.axis(axes)
    ax.yaxis.grid(True)
    # plt.grid(True)
    # plt.show()

    size_w = 12
    # size_h = size_w / 1.618
    size_h = 7
    fig.set_size_inches(size_w, size_h)

    plt.show()
    fig.savefig('plot.png')


bins1 = [0, 1, 2, 3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30]
axes1 = [0, 30, 0, 1900]
bins10 = [0, 10, 20, 30]
axes10 = [0, 30, 0, 9000]


def recursive_len(item):
    if type(item) == list:
        return sum(recursive_len(subitem) for subitem in item)
    else:
        return 1
# --------------------------------------end functions for plotting---------------------------------
# --------------------------------------end functions for plotting---------------------------------
# --------------------------------------end functions for plotting---------------------------------

def check_nb_sounds_in_data_split(data_set, var_name):
    # sanity check: total number of sounds
    accum_fsids = []
    for catid, sounds in data_set.items():
        accum_fsids += sounds

    print('Number of sounds in %s: %d' % (var_name, len(set(accum_fsids))))
    print('Number of categories: %d' % len(data_set))
    return 0


# ==================================HISTOGRAM OF CLIP DURATIONS=========================================================
# ======================================================================================================================


"""
report numbers to check all is good
"""
check_nb_sounds_in_data_split(data_dev, 'data_dev')
check_nb_sounds_in_data_split(data_dev_HQ, 'data_dev_HQ')
check_nb_sounds_in_data_split(data_eval, 'data_eval')
# all is good

if FLAG_PLOT:
    # # --histogram of clip durations for all clips of the dataset
    durations = [data_duration[str(id)]['duration'] for id in all_ids]
    fig_title = 'all clips in dataset: ' + str(len(durations))
    plot_histogram(durations, bins1, fig_title, axes1)
    # plot_histogram(durations, bins10, fig_title, axes10)

    # -- histogram of clip durations for all clips of DEVELOPMENT set----
    durations_dev = []
    for cat_id, sounds in data_dev.iteritems():
        durations_dev.extend([data_duration[str(fs_id)]['duration'] for fs_id in sounds])

    fig_title = 'all clips from DEV set: ' + str(len(durations_dev))
    plot_histogram(durations_dev, bins1, fig_title, axes1)
    # plot_histogram(durations_dev, bins10, fig_title, axes10)

    # -- histogram of clip durations for all clips of EVALUATION set----
    durations_eval = []
    for cat_id, sounds in data_eval.iteritems():
        durations_eval.extend([data_duration[str(fs_id)]['duration'] for fs_id in sounds])

    fig_title = 'all clips from EVAL set: ' + str(len(durations_eval))
    plot_histogram(durations_eval, bins1, fig_title, axes1)
    # plot_histogram(durations_eval, bins10, fig_title, axes10)



# ==================================BOX PLOTS=========================================================
# ======================================================================================================================


# ------------------- boxplot number of examples per category in dev / eval
nb_sounds_per_cat_dev = [len(sounds) for cat_id, sounds in data_dev.iteritems()]
nb_sounds_per_cat_eval = [len(sounds) for cat_id, sounds in data_eval.iteritems()]
data_plot = [nb_sounds_per_cat_dev, nb_sounds_per_cat_eval]
x_labels = ['dev', 'eval']
fig_title = 'number of audio samples in categories of dev and eval set'
y_label = '# of audio samples'
if FLAG_PLOT:
    plot_boxplot(data_plot,
                 x_labels,
                 fig_title,
                 y_label)

# DEVELOPMENT SET
# DEVELOPMENT SET

# -- # box plot of clip durations for every category for DEVELOPMENT set ----
names_all_cats_dev = []
durations_all_cats_dev = []

for cat_id, sounds in data_dev.iteritems():
    names_all_cats_dev.append(data_onto_by_id[cat_id]['name'])
    durations_dev_one_cat = [data_duration[str(fs_id)]['duration'] for fs_id in sounds]
    durations_all_cats_dev.append(durations_dev_one_cat)

# sort by ascending order by median
medians_cat = [np.median(cat) for cat in durations_all_cats_dev]
idx_durations_all_cats_dev = np.argsort(medians_cat)
durations_all_cats_dev_sorted = list(durations_all_cats_dev[val] for val in idx_durations_all_cats_dev)
names_all_cats_dev_sorted = list(names_all_cats_dev[val] for val in idx_durations_all_cats_dev)
fig_title = 'audio sample durations for every category DEV set -- all 41 categories'
y_label = 'duration [seconds]'
if FLAG_PLOT:
    plot_boxplot(durations_all_cats_dev_sorted,
                 names_all_cats_dev_sorted,
                 fig_title,
                 y_label)

# EVAL SET
# EVAL SET

# -- # box plot of clip durations for every low-level category for EVALUATION set after filtering----
names_all_cats_eval =  []
durations_all_cats_eval =  []

for cat_id, sounds in data_eval.iteritems():
    names_all_cats_eval.append(data_onto_by_id[cat_id]['name'])
    durations_dev_one_cat = [data_duration[str(fs_id)]['duration'] for fs_id in sounds]
    durations_all_cats_eval.append(durations_dev_one_cat)

# sort by ascending order by median
medians_cat = [np.median(cat) for cat in durations_all_cats_eval]
idx_durations_all_cats_eval = np.argsort(medians_cat)
durations_all_cats_eval_sorted = list(durations_all_cats_eval[val] for val in idx_durations_all_cats_eval)
names_all_cats_eval_sorted = list(names_all_cats_eval[val] for val in idx_durations_all_cats_eval)
fig_title = 'audio sample durations for every category EVAL set -- all 41 categories.'
if FLAG_PLOT:
    plot_boxplot(durations_all_cats_eval_sorted,
                 names_all_cats_eval_sorted,
                 fig_title,
                 y_label)


# ==================================BAR PLOTS=========================================================
# ======================================================================================================================

# DEVELOPMENT SET
# DEVELOPMENT SET

# -- # bar plot of number of HQ/LQ for every category for DEVELOPMENT set----
nb_sounds_per_cat_dev = []
nb_HQ_per_cat_dev = []
nb_LQ_per_cat_dev = []
names_all_cats_dev = []

names_all_cats_dev= [data_onto_by_id[cat_id]['name'] for cat_id, sounds in data_dev_HQ.iteritems()]
nb_sounds_per_cat_dev = [len(sounds) for cat_id, sounds in data_dev.iteritems()]
nb_HQ_per_cat_dev = [len(sounds) for cat_id, sounds in data_dev_HQ.iteritems()]
# are dicts read in the same order? it seems ok
# subtracting element wise in lists
nb_LQ_per_cat_dev = [i - j for i, j in zip(nb_sounds_per_cat_dev, nb_HQ_per_cat_dev)]

y_label = '# of audio samples'
fig_title = 'number of samples per category in DEV, split in HQ - LQ'
legenda = ('manually-verified', 'non-verified')
#

if FLAG_PLOT:
    plot_barplot_grouped(nb_HQ_per_cat_dev,
                         nb_LQ_per_cat_dev,
                         names_all_cats_dev,
                         y_label,
                         fig_title,
                         legenda,
                         260)


"""# plot para paper Task2 dcase18======================================================="""
"""ojo, nb_HQ_per_cat_dev_idx_alpha basado en data_dev_HQ, que igual esta mal

rehacer usando:
2018_Mar_14_FSDKaggle2018_delivered/dataset_dev.csv
pandas

"""

y_label = 'audio samples'

# alphabeticaly
idx_alpha =sorted(range(len(names_all_cats_dev)), key=lambda k: names_all_cats_dev[k])
names_all_cats_dev_idx_alpha = list(names_all_cats_dev[val] for val in idx_alpha)
nb_HQ_per_cat_dev_idx_alpha = list(nb_HQ_per_cat_dev[val] for val in idx_alpha)
nb_LQ_per_cat_dev_idx_alpha = list(nb_LQ_per_cat_dev[val] for val in idx_alpha)

if FLAG_PLOT:
    plot_barplot(nb_HQ_per_cat_dev_idx_alpha,
                 nb_LQ_per_cat_dev_idx_alpha,
                 names_all_cats_dev_idx_alpha,
                 y_label,
                 fig_title,
                 legenda,
                 305)
"""# end of plot para paper Task2 dcase18======================================================="""


# sorted accordin to the pycharm way
if FLAG_PLOT:
    plot_barplot(nb_HQ_per_cat_dev,
                 nb_LQ_per_cat_dev,
                 names_all_cats_dev,
                 y_label,
                 fig_title,
                 legenda,
                 305)

# say we want the classes in development set ordered by median of clip duration (consider only dev set)
names_all_cats_dev_sorted = list(names_all_cats_dev[val] for val in idx_durations_all_cats_dev)
nb_HQ_per_cat_dev_sorted = list(nb_HQ_per_cat_dev[val] for val in idx_durations_all_cats_dev)
nb_LQ_per_cat_dev_sorted = list(nb_LQ_per_cat_dev[val] for val in idx_durations_all_cats_dev)

if FLAG_PLOT:
    plot_barplot(nb_HQ_per_cat_dev_sorted,
                 nb_LQ_per_cat_dev_sorted,
                 names_all_cats_dev_sorted,
                 y_label,
                 fig_title,
                 legenda,
                 305)






# plot_barplot_grouped(nb_HQ_per_cat_dev_sorted,
#                      nb_LQ_per_cat_dev_sorted,
#                      names_all_cats_dev_sorted,
#                      y_label,
#                      fig_title,
#                      legenda,
#                      260)

# another option would be to group them by families, as in the excel



"""
find duration of each category in the DEV set, para paper Task2 dcase18
"""

total_dur = []
durations_perclass_dev = {}
for cat_id, sounds in data_dev.iteritems():
    # create key with cat name, and empyt list as value
    durations_perclass_dev[data_onto_by_id[cat_id]['name']] = []
    durations_perclass_dev[data_onto_by_id[cat_id]['name']].extend([data_duration[str(fs_id)]['duration'] for fs_id in sounds])
    print()
    print(data_onto_by_id[cat_id]['name'])
    # print(durations_perclass_dev[data_onto_by_id[cat_id]['name']])
    # print(sum(durations_perclass_dev[data_onto_by_id[cat_id]['name']]))
    n_min = sum(durations_perclass_dev[data_onto_by_id[cat_id]['name']])/60.0
    print(n_min)
    total_dur.append(n_min)

print("\ntotal duration in hours:")
print(sum(total_dur)/60.0)



"""# plot para Tuomas slides con teams ranking of Task2 dcase18====================================================="""

mAPs = [0.953811, 0.951245, 0.949833, 0.949577, 0.943546, 0.942263, 0.941878,
        0.941365, 0.940467, 0.932769, 0.927508, 0.918784, 0.915063, 0.906467,
        0.889659, 0.877469, 0.789838, 0.697844, 0.694251]

x_labels = ['Cochlear.ai','Surrey CVSSP','NUDT','Emilia_NTU', 'Deep Lake', 'kuaiyu', 'kardec',
            'Kevin Wilkinghoff', 'Ducky', 'gyat', 'Iurii Agafonov', 'Frederic Chopin', 'GIST_WisenetAI', 'FishGhost',
            'NTU_r06725026', 'yuer', 'Grenade', 'Fred', 'Baseline']

y_label = 'mAP @ private leaderboard'
plot_barplot_simple(mAPs,
                    x_labels,
                    y_label,
                    fig_title,
                    1.01)

# unknown people from the excel that we matched to the LB by computing private mAPs and comparing to LB
# ============================================

# 'Fred' 0.697844

# Maxim Khadkevich report, team Frederic chopin in kaggle
# Number of PRIVATE files evaluated: 1299, matches Frederic chopin
# MAP_3 for PRIVATE files evaluated: 0.918784
#
# Number of PUBLIC files evaluated: 301
# MAP_3 for PUBLIC files evaluated: 0.913068

# Number of PRIVATE files evaluated: 1299, does not match anything, maybe he got confused.
# MAP_3 for PRIVATE files evaluated: 0.917757
#
# Number of PUBLIC files evaluated: 301
# MAP_3 for PUBLIC files evaluated: 0.910299
# Backend TkAgg is interactive backend. Turning interactive mode on.


# 'Ducky' 0.940467

# Number of PRIVATE files evaluated: 1299
# MAP_3 for PRIVATE files evaluated: 0.940467
#
# Number of PUBLIC files evaluated: 301
# MAP_3 for PUBLIC files evaluated: 0.973422

# esta es mayor, pero no es la que mando a kaggle (a dcase si el perro de el)
# Number of PRIVATE files evaluated: 1299
# MAP_3 for PRIVATE files evaluated: 0.942263
#
# Number of PUBLIC files evaluated: 301
# MAP_3 for PUBLIC files evaluated: 0.971761

"""# END of plot para Tuomas slides con teams ranking of Task2 dcase18=============================================="""

a=9