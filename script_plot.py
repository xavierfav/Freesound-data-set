# PRINT VOTES
votes_TT = pickle.load(open('votes_TT_all.pkl','rb'))
for i in votes_TT:
    print i[1].ljust(110) + str(i[2]).ljust(10) + str(i[3]).ljust(10)  + str(i[4]).ljust(10)  + str(i[5]).ljust(10) + str(i[6]).ljust(10)+ str(i[7]).ljust(10) + str(i[8])


# PLOT P NP
# index of changes of category
lines_coord = [0,44, 64, 119, 207, 224, 358, 398]
# category group names
lines_names = ['Animal', 'Channel, environment and background', 'Human sounds', 'Music', 'Natural sounds', 'Sounds of things', 'Source-ambiguous sounds']

sns.set(style="whitegrid")
x = range(len(votes_TT)) 
v_np = [i[5] for i in votes_TT] # extract non present votes
v_p =[i[2] + i[3] for i in votes_TT] # extract present votes
plt.bar(x, [-v for v in v_np], facecolor='#ff9999', edgecolor='white') # plot NP votes negative
plt.bar(x, v_p, facecolor='#9999ff', edgecolor='white') # plot P votes 
# plot the lines delimiting categories groups
for idx, name in enumerate(lines_names):
    line = np.linspace(lines_coord[idx]+1, lines_coord[idx+1]+1)
    line_y = 0*line - 200
    plt.plot(line,line_y)
    line = np.linspace(-200,500)
    line_y = 0*line + lines_coord[idx+1]+1
    plt.plot(line_y, line, color='black', linewidth=0.5)
plt.show()


# PLOT U
sns.set(style="whitegrid")
plt.bar(x, v_u, facecolor='#9999ff', edgecolor='white')
for idx, name in enumerate(lines_names):
    line = np.linspace(lines_coord[idx]+1, lines_coord[idx+1]+1)
    line_y = 0*line - 50 
    plt.plot(line,line_y)
    line = np.linspace(-50,100)
    line_y = 0*line + lines_coord[idx+1]+1
    plt.plot(line_y, line, color='black', linewidth=0.5)
plt.show()


# PRINT NUM UNSURE PER GROUP CATEGORY
for idx,i in enumerate(lines_coord[:-1]):
    print sum([i[4] for i in votes_TT[i:lines_coord[idx+1]]])

for idx,i in enumerate(lines_coord[:-1]):
    print sum([i[4] for i in votes_TT[i:lines_coord[idx+1]]])/float((lines_coord[idx+1]-lines_coord[idx]))
