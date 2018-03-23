

# Freesound Dataset Kaggle 2018 (FSDKaggle2018)


## About this dataset

Freesound Dataset Kaggle 2018 (or **FSDKaggle2018** for short) is an audio dataset containing ~19k audio files annotated with labels of the AudioSet Ontology [1].

All audio samples in this dataset are gathered from Freesound [2] and are provided here as uncompressed PCM 16 bit, 44.1 kHz, mono audio files. All sounds in Freesound are released under Creative Commons Licenses. For attribution purposes and to facilitate attribution of these files to third parties, this dataset includes a relation of audio files and their corresponding license. The file with the relation of licenses will be published only after the competition is concluded in order to ensure data anonymity during the competition. (see [What's contained in this folder](#What's-in-this-folder) section).

Ground truth data has been obtained after a data labeling process which is [described below](#Data-labeling-process). More details about the process can be found in [3].

**FSDKaggle2018** contains a total amount of 18873 audio samples, unequally distributed among **41 categories** from the AudioSet Ontology, including musical instruments, human sounds, domestic sounds, animals, etc. Here are some relevant characteristics of FSDKaggle2018:

* A total amount of 18873 audio samples, unequally distributed among 41 categories taken from the AudioSet Ontology.
* **5310** of the ground truth labels have been **manually verified** by human annotators (some of the labels have inter-annotator agreement but not all of them) while the **the rest has not been manually verified**. However, the non-verified audio clips still present Freesound tags related to the category under consideration. Checkout the [Data labeling process](#Data-labeling-process) section for more information about this aspect.
* The dataset it split into a **development set** and an **evaluation set**.
* The **development set** is composed of ~3.7k manually-verified annotations, along with ~5.8k non-verified annotations. The quality of these non-verified annotations in the development set has been roughly estimated to be at least 65-70% in each category. Checkout the [Data labeling process](#Data-labeling-process) section for more information about this aspect. Thus, the development set has an amount of ~9.5k samples, with approximately 61% (5.8k/9.5k) non-verified labels. 
* A flag in the `dataset_dev.csv` file indicates whether or not every annotation in the development set has been manually verified, so that participants can use this information during the development of their systems. See [What's contained in this folder](#What's-in-this-folder) section.
* Around 50% of the categories feature more non-verified samples than verified samples in the development set. On the contrary, around 25% of the categories have a similar amount of verified and non-verified samples, while the remaining 25% of the categories present more verified samples than non-verified ones in the development set.
* The **evaluation set** is composed of the remaining ~1.6k manually-verified annotations, along with a number of non-verified annotations. The evaluation metric for systems ranking will be computed using the manually-verified portion only.
* All audio samples in this dataset have a single label (i.e. they are only annotated with one label). A single label should be predicted for each file in the evaluation set.
* The minimum number of audio samples per category in the development set is 94, the maximum is 300.
* The duration of the audio samples ranges from 300ms to 30s. 
* The total duration of the development set is roughly 18h.
* The total duration of the manually verified part of the evaluation set is roughly 2h.

## What's contained in this folder

* `readme.md`

* `dev/`
 * `dataset_dev.csv`: CSV file with ground truth information for the development set of FSDKaggle2018.
 * `audio/`: Folder with audio files. All files are in the same directory, with filename `SOUND_ID.wav` (16bit, 44.1kHz, mono).
 * `licenses_dev.txt`: List of licenses for each audio file included in the split. This file will be published **only** after the competition is concluded.

* `eval/`
 * `dataset_eval.csv`: CSV file with the list of audio samples for the evaluation set of FSDKaggle2018. The ground truth for this split will be published **only** after the competition is concluded.
 * `audio/`: Folder with audio files. All files are in the same directory, with filename `SOUND_ID.wav` (16bit, 44.1kHz, mono).
 * `licenses_eval.txt`: List of licenses for each audio file included in the split. This file will be published only after the competition is concluded.


Both `dataset_dev.csv` and `dataset_eval.csv` are CSV files (comma-delimited). `dataset_dev.csv` presents 4 columns indicating the following information:

1. **Sound ID**: Unique identifier for an audio sample. It is a fake Freesound id to ensure data anonymity during the competition.
2. **FSDKaggle2018 Ground truth AudioSet Ontology category ID**: Ground truth category *identifier* as defined in the AudioSet Ontology. For example `/m/028ght`.
3. **FSDKaggle2018 Ground truth AudioSet Ontology category name**: Ground truth category *name* as defined in the AudioSet Ontology. For example `Applause` (which corresponds to `/m/028ght`).
4. **Verified annotation flag**: Boolean (1 or 0) flag to indicate whether or not that annotation has been manually verified.

Therefore, **columns 2 and 3** of `dataset_dev.csv` are the ground truth for the development set of FSDKaggle2018.

`dataset_eval.csv` presents 1 column indicating the following information:

1. **Sound ID**: Unique identifier for an audio sample. It is a fake Freesound id to ensure data anonymity during the competition.


## Data labeling process

The data labeling process started from a manual mapping between Freesound tags and AudioSet Ontology concepts which was carried out by researchers at the Music Technology Group, Universitat Pompeu Fabra. Using this mapping, we could **automatically annotate Freesound audio samples** with concepts from the AudioSet Ontology. These annotations can be understood as weak labels since they express the presence of a sound category in an audio sample. 

Then, we followed a data validation process in which a number of participants did listen to the annotated sounds and manually asses the presence/absence of an automatically assigned sound category, according to the AudioSet description of the category. For each sound/category pair, participants could select one of the following options:

* **Present and predominant (PP).** The category of sound described is clearly present and predominant. This means there are no other types of sound, with the exception of low/mild background noise. 
* **Present but not predominant (PNP).** The category of sound described is present, but the audio sample also contains other salient types of sound and/or strong background noise. 
* **Not Present (NP).** The category of sound described is not present in the audio sample. 
* **Unsure (U).** It is not clear whether the category of sound is present or is not present in the audio sample.

Audio samples in FSDKaggle2018 are only assigned a single label. A total of **5310** labels included in FSDKaggle2018 have been **manually validated as PP** (some with inter-annotator agreement but not all of them). This means that in most cases there is no additional acoustic material other than the labeled category. In a few cases there may be some additional events, typically with lower level and out of the set of the 41 classes of FSDKaggle2018. Thus, these manually verified samples bear only one label (which is the one provided as ground truth).

The rest of the labels have **not** been manually validated. Therefore it can be expected that some will be inaccurate. Nonetheless, we have roughly estimated that **at least 65-70% of the non-verified labels per category in the development set are indeed correct**. In some occasions, the non-verified samples could present multiple sound categories (often beyond the list of 41 categories) even though only one label is provided.


## References

[1] Jort F Gemmeke, Daniel PW Ellis, Dylan Freedman, Aren Jansen, Wade Lawrence, R Channing Moore, Manoj Plakal, and Marvin Ritter. "Audio set: An ontology and human-labeled dartaset for audio events." Proceedings of the Acoustics, Speech and Signal Pro- cessing International Conference, 2017.

[2] Frederic Font, Gerard Roma, and Xavier Serra. "Freesound technical demo." Proceedings of the 21st ACM international conference on Multimedia, 2013. [https://freesound.org](https://freesound.org)

[3] Eduardo Fonseca, Jordi Pons, Xavier Favory, Frederic Font, Dmitry Bogdanov, Andres Ferraro, Sergio Oramas, Alastair Porter, and Xavier Serra. "Freesound Datasets: A Platform for the Creation of Open Audio Datasets." Proceedings of the International Conference on Music Information Retrieval, 2017. [PDF here](https://ismir2017.smcnus.org/wp-content/uploads/2017/10/161_Paper.pdf)

