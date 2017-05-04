import pickle
import json
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

# PRINT VOTES
#votes_TT = pickle.load(open('votes_TT_all.pkl','rb'))
votes_TT = pickle.load(open('votes_new2.pkl','rb'))

# PLOT P NP
# index of changes of category
lines_coord = [0, 45, 65, 120, 208, 225, 359]
lines_coord_end = [44, 64, 119, 207, 224, 358, 397]
# category group names
lines_names = ['Animal', 'Channel, environment and background', 'Human sounds', 'Music', 'Natural sounds', 'Sounds of things', 'Source-ambiguous sounds']

sns.set(style="whitegrid")
ax = plt.axes()        
ax.xaxis.grid()
x = range(len(votes_TT)) 
votes_TT = sorted(votes_TT, key=lambda c: c[2]+c[3])

v_np = [i[5] for i in votes_TT] # extract non present votes
v_pp = [i[2] for i in votes_TT] # extract present and predominant votes
v_pnp = [i[3] for i in votes_TT] # extract present but not predominant votes
v_u = [i[4] for i in votes_TT] # extract usure votes

#normalized
#v_np = [i[5]/float(i[6]) for i in votes_TT] # extract non present votes
#v_pp = [i[2]/float(i[6]) for i in votes_TT] # extract present and predominant votes
#v_pnp = [i[3]/float(i[6]) for i in votes_TT] # extract present but not predominant votes
#v_u = [i[4]/float(i[6]) for i in votes_TT] # extract usure votes

p1 = plt.bar(x, v_pp, facecolor='#4242c5', edgecolor='#4242c5') # plot PP votes 
p2 = plt.bar(x, v_pnp, facecolor='#8989ec', edgecolor='#8989ec', bottom=v_pp) # plot PNP votes 
p3 = plt.bar(x, [-v for v in v_np], facecolor='#e33434', edgecolor='#e33434') # plot NP votes negative
p4 = plt.bar(x, [-v for v in v_u], facecolor='#ee8080', edgecolor='#ee8080', bottom=[-v for v in v_np]) # plot U votes negative

# plot the lines delimiting categories groups
for idx, name in enumerate(lines_names):
    if idx%2 == 0:
        plt.axvspan(lines_coord[idx]-0.1, lines_coord_end[idx]+0.9, facecolor='0.5', alpha=0.1)

# limit axis
#plt.xlim(0,398)
plt.ylim(-300,420)

# fix counts axis positive values
ax.set_yticklabels([str(int(abs(x))) for x in ax.get_yticks()],fontsize=15)

# add legends
plt.legend((p1[0], p2[0], p3[0], p4[0]), ('PP', 'PNP', 'NP', 'U'),fontsize=15)

# add titles
ax.set_xlabel('Categories', fontsize=15)
ax.set_ylabel('Vote counts', fontsize=15)
#plt.title('Super nice plot', fontsize=20)

# plot
plt.savefig('votes.pdf', format='pdf')
plt.show()



