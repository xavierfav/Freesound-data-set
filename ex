launch ipython

run tools.py

# to get most cooccurrencing tags (Works for a unique term only)
get_relevant_tags('pig')[:200] 

# use freesound website also if you want

# fill the ontology_tags dict
# ontology_tags[<node_id>] = <list of relevant tags>

ontology_tags[ontology_by_name['Pig']['id']] = ['pig', 'hog']


# ontology_by_name['Pig']['id'] can be used to get the id from the name of the node

# for classes like "Medium engine", figure out what it means using the description in the ontology and then look for the terms that seems to be relevant

# When several FS tags are needed to be equivalent to the Audio Set class, use lists of lists: [['rocket', 'engine'], 'rocket-engine']
