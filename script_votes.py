import json
import pickle
import matplotlib.pyplot as plt
import numpy as np

# load votes (got it from FSD local)
votes_sounds_annotation = json.load(open('votes_sounds_annotations.json','rb'))

# load old votes_TT
votes_TT = pickle.load(open('votes_TT_new.pkl','rb'))

# filter duplicates
v = [(vv['freesound'], vv['freesound_sound_id'], vv['node_id'], vv['value']) for vv in votes_sounds_annotation]
v_filter = list(set(v))

votes = []
# extract votes
for node in votes_TT:
    count_PP = len([i for i in v_filter if i[2]==node[0] and i[3]==1])
    count_PNP = len([i for i in v_filter if i[2]==node[0] and i[3]==0.5])
    count_U = len([i for i in v_filter if i[2]==node[0] and i[3]==0])
    count_NP = len([i for i in v_filter if i[2]==node[0] and i[3]==-1])
    count_total = count_PP + count_PNP + count_U + count_NP
    votes.append((node[0], node[1], count_PP, count_PNP, count_U, count_NP, count_total, node[7]))

pickle.dump(votes, open('votes_new2.pkl','w'))


# caculate stats
sounds = json.load(open('FS_sounds_ASO_postIQA.json','rb'))

# list 398 node_id
node_set = set([i[0] for i in votes])

total_PP = sum([v[2] for v in votes])
total_PNP = sum([v[3] for v in votes])
total_P = total_PP + total_PNP
total_U = sum([v[4] for v in votes])
total_NP = sum([v[5] for v in votes])

vote_PP = [i for i in v_filter if i[3]==1 and i[2] in node_set]
vote_PNP = [i for i in v_filter if i[3]==0.5 and i[2] in node_set]
vote_U = [i for i in v_filter if i[3]==0 and i[2] in node_set]
vote_NP = [i for i in v_filter if i[3]==-1 and i[2] in node_set]

# sounds from mapping
sounds = json.load(open('FS_sounds_ASO_postIQA.json','rb'))

sounds_PP = list(set([i[1] for i in vote_PP]))
sounds_PNP = list(set([i[1] for i in vote_PNP]))
sounds_P = list(set(sounds_PP + sounds_PNP))
sounds_U = list(set([i[1] for i in vote_U]))
sounds_NP = list(set([i[1] for i in vote_NP]))
sounds_all = list(set(sounds_PP + sounds_PNP + sounds_U + sounds_NP))

length_PP = [sounds[str(k)]['duration'] for k in  sounds_PP]
length_PNP = [sounds[str(k)]['duration'] for k in  sounds_PNP]
length_P = [sounds[str(k)]['duration'] for k in  sounds_P]
length_U = [sounds[str(k)]['duration'] for k in  sounds_U]
length_NP = [sounds[str(k)]['duration'] for k in  sounds_NP]
length_all_validated = [sounds[str(k)]['duration'] for k in  sounds_all]
length_all_mapping = [sounds[str(k)]['duration'] for k in sounds.keys()]


# histogram length
names = ['PP', 'P', 'all']
for idx, hist_len in enumerate([length_PP, length_P, length_all_mapping]):
    plt.figure()
    plt.hist(hist_len, bins=np.arange(np.array(hist_len).min(), np.array(hist_len).max()), cumulative=True, normed=1., alpha = 0.5)
    plt.title('Histogram length sounds ' + names[idx] + ' cumulative')
    plt.xlabel("Value")
    plt.ylabel("Ratio")
    plt.grid(True)
    axes = plt.gca()
    axes.set_ylim([0,1])
    plt.show()
    #plt.savefig('hist_lenght_' + names[idx] + '_cumulative')

    plt.figure()
    plt.hist(hist_len, bins=np.arange(np.array(hist_len).min(), np.array(hist_len).max(), 5), normed=1., alpha = 0.5)
    plt.title('Histogram length sounds ' + names[idx])
    plt.xlabel("Value")
    plt.ylabel("Ratio")
    plt.grid(True)
    plt.show()
    #plt.savefig('hist_lenght_' + names[idx] + '_normed')

    plt.figure()
    plt.hist(hist_len, bins=np.arange(np.array(hist_len).min(), np.array(hist_len).max(), 5), alpha = 0.5)
    plt.title('Histogram length sounds ' + names[idx] + ' absolute')
    plt.xlabel("Value")
    plt.ylabel("Amount")
    plt.grid(True)
    plt.show()
    #plt.savefig('hist_lenght_' + names[idx] + '_absolute')


