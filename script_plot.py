import pickle
import json
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

# PRINT VOTES
#votes_TT = pickle.load(open('votes_TT_all.pkl','rb'))
votes_TT = pickle.load(open('votes/votes_new2.pkl','rb'))
nb_access_FS_per_category_dict = json.load(open('figures_and_co/nb_access_FS_per_category_dict', 'rb'))
for i in votes_TT:
    print i[1].ljust(110) + str(i[2]).ljust(10) + str(i[3]).ljust(10)  + str(i[4]).ljust(10)  + str(i[5]).ljust(10) + str(i[6]).ljust(10)+ str(i[7]).ljust(10)# + str(i[8])

for i in votes_TT:
    print i[1].ljust(110) + str("{0:.2f}".format(i[2]/float(i[6]))).ljust(10) + str("{0:.2f}".format(i[3]/float(i[6]))).ljust(10)  + str("{0:.2f}".format(i[4]/float(i[6]))).ljust(10)  + str("{0:.2f}".format(i[5]/float(i[6]))).ljust(10) + str(i[6]).ljust(10)+ str(i[7]).ljust(10)# + str(i[8])


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
#votes_TT = sorted(votes_TT, key=lambda c: c[2]+c[3])

v_np = [i[5] for i in votes_TT] # extract non present votes
v_pp = [i[2] for i in votes_TT] # extract present and predominant votes
v_pnp = [i[3] for i in votes_TT] # extract present but not predominant votes
v_u = [i[4] for i in votes_TT] # extract usure votes
access_FS_order = [nb_access_FS_per_category_dict[i[0]] for i in votes_TT]

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
plt.xlim(0,398)
plt.ylim(-300,420)

# fix counts axis positive values
ax.set_yticklabels([str(int(abs(x))) for x in ax.get_yticks()],fontsize=20, fontweight="bold")
ax.set_xticklabels([str(int(x)) for x in ax.get_xticks()], fontsize=19, fontweight="bold")

# add legends
plt.legend((p1[0], p2[0], p3[0], p4[0]), ('PP', 'PNP', 'NP', 'U'),fontsize=20)

# add titles
ax.set_xlabel('Categories', fontsize=20, fontweight="bold")
ax.set_ylabel('Vote counts', fontsize=20, fontweight="bold")
#plt.title('Super nice plot', fontsize=20)

plt.tight_layout()

# plot
plt.savefig('votes.pdf', format='pdf')
plt.show()


# PLOT ACCESS FS
sns.set(style="whitegrid")
ax = plt.axes()        
ax.xaxis.grid()
x = range(len(votes_TT)) 
p1 = plt.bar(x, access_FS_order, facecolor='#6e6ef6', edgecolor='white')
# plot the lines delimiting categories groups
for idx, name in enumerate(lines_names):
    if idx%2 == 0:
        plt.axvspan(lines_coord[idx]-0.1, lines_coord_end[idx]+0.9, facecolor='0.5', alpha=0.1)
# limit axis
plt.xlim(0,398)
# add titles
ax.set_xlabel('Categories')
ax.set_ylabel('Access FS count')
plt.title('Super nice plot', fontsize=20)
plt.show()



# EX: PRINT NUM xxx PER GROUP CATEGORY
for idx,_ in enumerate(lines_coord):
    print sum([i[2] for i in votes_TT[lines_coord[idx]:lines_coord_end[idx]+1]])

print '\n'
for idx,o in enumerate(lines_coord):
    print sum([i[4] for i in votes_TT[o:lines_coord_end[idx]]])/float((lines_coord_end[idx]-lines_coord[idx]))

print '\n'
for idx,o in enumerate(lines_coord):
    print sum([i for i in access_FS_order[o:lines_coord_end[idx]]])/float(sum([v[6] for v in votes_TT[o:lines_coord_end[idx]]]))

for idx,i in enumerate(votes_TT):                                                
    print i[1].ljust(110) + str(access_FS_order[idx]/float(i[6]))


