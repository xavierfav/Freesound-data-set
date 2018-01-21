# Freesound-data-set


IMPORTANT FOLDERS:
- kaggle2/ is the dataset FSD9k split in development/evaluation 70/30 %. This is the final version sent to Kaggle (except that in the format conversion we lost 3 audio clips in the dev set and 3 others in the eval set (6 clips in total, with respect to what the proposal says)
- kaggle/ is a previous attempt for dataset split, using development/evaluation 60/40 %. We discarded this slipt in favour of kaggle2/ to increase development set size.

ANNOTATION:

Need to add this files in order to use tools.py for annotations:
- tag_cooccurrences.pkl
https://drive.google.com/open?id=0B6I4aBwnXxoGY2Z5dG5vdnlwSGM
- tag_to_idx_cooc_matrix.pkl
https://drive.google.com/open?id=0B6I4aBwnXxoGU2NpU3pwSGNWbms

ex file provide a example of how to use annotation tools.
For now each annotator will provide an ontology_***.json file with his annotation.




LABELLING FREESOUND SOUNDS:

Need 'freesound_db_030317' pickle file placed in folder ./baskets_pickle/
https://drive.google.com/open?id=0B6I4aBwnXxoGU2xmakRwaS1OUWM

manager.py: tool for playing with freesound stuff
freesound.py: freesound python api wrapper
https://github.com/xavierfav/freesound-python
(The functions and object are documented, if you use iPython use <instance>?)


dependencies:

>>> virtualenv venv

>>> source virtualenv/bin/activate

>>> pip install -r requirements


run script: (needs a bit of memory for loading all Freesound metadata, close your browser tabs...)

>>> ipython

>>> run sound_labelling.py

_______________________________________


PLOT STATS:

The script_plot.py contains the code for reproducing the basic plots and prints.
The data is in the 'votes_TT_all.pkl' file structured like that:
[(<id>, <name>, <#PP>, <#PNP>, <#U>, <#NP>, <#Votes>, <#Annotations>, <#Votes left to 72>), ...]

The different Prints and Plots:
- Print of the votes for each node (Name, #PP, #PNP, #U, #NP, #Total Votes, #Annotations, #Votes to 72)
- Plot of Present and Non Present 
- Plot of Unsure
- Print # Unsure per group category 

_______________________________________

DATA CHARACTERIZATION:

We have plots for analyzing:
- Distribution (histograms) of clip durations for several subsets (all, dev, eval, PP, PNP)
- boxplots:
 - clip duration in PP/PNP
 - clip duration for every category in dev/eval (for leaves and high-level categories after merging)
 - number of clips per category in dev/eval
- barplots:
 - number of votes (sounds) per category, split into PP and PNP, for dev/eval, with different sortings

