

# Freesound Dataset Kaggle 2018 (FSDKaggle2018)


## About this dataset


Freesound Dataset Kaggle 2018 (or **FSDKaggle2018** for short) is an audio dataset containing ~19k audio files annotated with labels of the AudioSet Ontology [1].

All audio samples in this dataset are gathered from Freesound [2] and are provided here as uncompressed PCM 16 bit, 44.1 kHz, mono audio files. All sounds in Freesound are released under Creative Commons Licenses. For attribution purposes and to facilitate attribution of these files to third parties, this dataset includes a relation of audio files and their corresponding license. The file with the relation of licenses will be published after the competition is concluded in order to ensure data anonymity during the competition. (see [What's in this folder](#What's-in-this-folder) section).

Ground truth data has been obtained after a data labeling process which is [described below](#data-labeling-process). More details about the process can be found in [3].

**FSDKaggle2018** contains a total amount of 18873 audio samples, unequally distributed among **41 categories** from the AudioSet Ontology. Here are some relevant characteristics of FSDKaggle2018:

* A total amount of 18873 audio samples, unequally distributed among 41 categories taken from the AudioSet Ontology.
* 5310 of the ground truth labels have been **manually verified** by human annotators, while the others have not been manually verified. Checkout the [data labeling process](#data-labeling-process) section below for more information about this aspect.
* The dataset it split into a **development set** and an **evaluation set**.
* The **development set** is composed of ~3.7k (roughly 70%) of the manually verified annotations per category, plus ~5.8k non-verified annotations. The non-verified annotations of the development set have a quality estimate of at least 65-70%. Checkout the [data labeling process](#data-labeling-process) section below for more information about this aspect.
* The **evaluation set** is composed of the remaining ~1.6k (roughly 30%) of the verified annotations per category, along with ~7.8k of the non-verified annotations. The evaluation metric for systems ranking will be computed based on the manually verified annotations only.
* The minimum number of audio samples per category in the development set is 94, the maximum is 300.
* The minimum number of manually verified audio samples per category in the evaluation set is 25, the maximum is 110.
* All audio samples in this dataset have a single label (i.e. are only annotated with one label).
* The duration of the audio samples ranges from 300ms to 30s. 
* The total duration of the development set is roughly 18h.
* The total duration of the manually verified part of the evaluation set is roughly 2h.

## What's contained in this folder

* `readme.md`

* `dev/`
 * `dataset_dev.csv`: CSV file with ground truth information for FSDKaggle2018 (only includes ground truth for development set).
 * `audio/`: Folder with audio files. All files are in the same directory, with filename `SOUND_ID.wav` (16bit, 44.1kHz, mono).
 * `licenses_dev.txt`: List of licenses for each audio file included in the split. This file will be published after the competition is concluded.

* `eval/`
 * `dataset_eval.csv`: CSV file with ground truth information for FSDKaggle2018 (only includes ground truth for evaluation set).
 * `audio/`: Folder with audio files. All files are in the same directory, with filename `SOUND_ID.wav` (16bit, 44.1kHz, mono).
 * `licenses_eval.txt`: List of licenses for each audio file included in the split. This file will be published after the competition is concluded.


Both `dataset_dev.csv` and `dataset_eval.csv` are CSV files (comma-delimited) with 4 columns indicating the following information:

1. **Sound ID**: Unique identifier for an audio sample. It is a fake Freesound id to ensure data anonymity during the competition.
2. **FSDKaggle2018 Ground truth AudioSet Ontology category ID**: Ground truth category *identifier* as defined in the AudioSet Ontology. For example `/m/028ght`.
3. **FSDKaggle2018 Ground truth AudioSet Ontology category name**: Ground truth category *name* as defined in the AudioSet Ontology. For example `Applause` (which corresponds to `/m/028ght`).
4. **Verified annotation flag**: Boolean (1 or 0) flag to indicate whether or not that annotation has been manually verified.

Therefore, **columns 2 and 3** are the ground truth for FSDKaggle2018.


## Data labeling process

The data labeling process started from a manual mapping between Freesound tags and AudioSet Ontology concepts which was carried out by researchers at the Music Technology Group, UPF. Using this mapping, we could **automatically annotate Freesound audio samples** with concepts from the AudioSet Ontology. These annotations can be understood as weak labels since they express the presence of a sound category in an audio sample. 

Then, we followed a data validation process in which a number of participants did listen to the annotated sounds and manually asses the presence/absence of an automatically assigned sound category. For each sound/category pair, participants could select one of the following options:

* **Present and predominant (PP).** The category of sound described is clearly present and predominant. This means there are no other types of sound, with the exception of low/mild background noise. 
* **Present but not predominant (PNP).** The category of sound described is present, but the audio sample also contains other salient types of sound and/or strong background noise. 
* **Not Present (NP).** The category of sound described is not present in the audio sample. 
* **Unsure (U).** It is not clear whether the category of sound is present or is not present in the audio sample.

A total of **5310** annotations included in FSDKaggle2018 are annotations that have been **manually validated as PP**. Some of them feature inter-annotator agreement but not all of them.

The rest of the annotations have **not** been manually validated. Nonetheless, we have **roughly estimated** that at least 65-70% of the non-verified annotations per category **in the development set** are indeed correct. It is thus to be expected that some labels will be inaccurate or inconsistent in the development set.

Audio samples in FSDKaggle2018 are only assigned a single label. The manually verified samples bear only this one label out of the set of 41 categories of FSDKaggle2018, according to the AudioSet description of the category. However, the non verified samples could present multiple sound events/categories in some occasions, even though only one label is provided.


## References

[1] Jort F Gemmeke, Daniel PW Ellis, Dylan Freedman, Aren Jansen, Wade Lawrence, R Channing Moore, Manoj Plakal, and Marvin Ritter. "Audio set: An ontology and human-labeled dartaset for audio events." Proceedings of the Acoustics, Speech and Signal Pro- cessing International Conference, 2017.

[2] Frederic Font, Gerard Roma, and Xavier Serra. "Freesound technical demo." Proceedings of the 21st ACM international conference on Multimedia, 2013. [https://freesound.org](https://freesound.org)

[3] Eduardo Fonseca, Jordi Pons, Xavier Favory, Frederic Font, Dmitry Bogdanov, Andres Ferraro, Sergio Oramas, Alastair Porter, and Xavier Serra. "Freesound Datasets: A Platform for the Creation of Open Audio Datasets." Proceedings of the International Conference on Music Information Retrieval, 2017. [PDF here](https://ismir2017.smcnus.org/wp-content/uploads/2017/10/161_Paper.pdf)

