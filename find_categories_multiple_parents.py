import json
import numpy as np


with open('ontology.json') as data_file:
	data = json.load(data_file)

categories_with_several_parents_id = []
categories_with_several_parents_name = []

for i in np.arange(len(data)):
	print i
	target_id = data[i]['id'] #grab every category

	# reset counter
	count=0

	for k in np.arange(len(data)):
		if target_id in data[k]['child_ids']:
			print target_id + ', with name ' +  data[i]['name']  + ' is a child'
			count+=1
			print (count)



	if count>1:
		print '----------a standard category can be ONLY one child of ONE parent, or none if it is at top level'
		categories_with_several_parents_id.append(target_id)
		categories_with_several_parents_name.append(data[i]['name'])
		print (target_id)
		print ('------------')
		print()

print '\n--list all cats with more than one parent: \n'
for idx,name in enumerate(categories_with_several_parents_name):
	print idx,name


# --list all cats with more than one parent

# 0 Children shouting
# 1 Choir
# 2 Chant
# 3 Clapping
# 4 Hubbub, speech noise, speech babble
# 5 Howl
# 6 Growling
# 7 Hiss
# 8 Clip-clop
# 9 Cowbell
# 10 Bleat
# 11 Chirp, tweet
# 12 Buzz
# 13 Rattle
# 14 Bell
# 15 Bicycle bell
# 16 Beatboxing
# 17 Wind noise (microphone)
# 18 Crackle
# 19 Vehicle horn, car horn, honking
# 20 Car alarm
# 21 Air horn, truck horn
# 22 Police car (siren)
# 23 Ambulance (siren)
# 24 Fire engine, fire truck (siren)
# 25 Jet engine
# 26 Dental drill, dentist's drill
# 27 Doorbell
# 28 Knock
# 29 Tap
# 30 Squeak
# 31 Kettle whistle
# 32 Tick
# 33 Crack
# 34 Snap
# 35 Squish
# 36 Whoosh, swoosh, swish
# 37 Thump, thud



