# Freesound-data-set

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
https://drive.google.com/open?id=0B6I4aBwnXxoGRUk5b201NlZTazQ

manager.py: tool for playing with freesound stuff
freesound.py: freesound python api wrapper
https://github.com/xavierfav/freesound-python


dependencies:

>>> virtualenv venv

>>> source virtualenv/bin/activate

>>> pip install -r requirements


run script:
Need the ontology json file with fs_tags fields from annotations

>>> ipython

>>> run sound_labelling.py

