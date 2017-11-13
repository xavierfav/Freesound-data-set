import json
import xlsxwriter
import matplotlib.pyplot as plt
import numpy as np


MIN_QUALITY = 50
MIN_EXAMPLES = 6
MAX_ACCESSS_FS = 5

def get_parents(aso_id, ontology):
    parents = []
    ontology_by_id = {o['id']:o for o in ontology}
    # 1st pass for direct parents
    for o in ontology:
        for id_child in o["child_ids"]:
            if id_child == aso_id:
                parents.append(o['id'])
    return [ontology_by_id[parent] for parent in parents]

def get_all_parents(aso_id, ontology): 
    """ 
    Recursive method to get the parents chain for an aso category
    """
    ontology_by_id = {o['id']:o for o in ontology}
    def paths(node_id, cur=list()):
        parents = get_parents(node_id, ontology)
        if not parents:
            yield cur
        else:
            for node in parents:
                for path in paths(node['id'], [node['name']] + cur):
                    yield path
    return paths(aso_id)

def plot_histograms(stats):
    hist_quality = []
    hist_nb_ex = []
    hist_fs_access = []
    for s in stats:
        if stats[s][0]>0:
            hist_quality.append(stats[s][0])
            hist_nb_ex.append(stats[s][1])
            hist_fs_access.append(stats[s][2])
    plt.subplot(3, 1, 1)
    plt.hist(hist_quality, bins=np.arange(np.array(hist_quality).min(), np.array(hist_quality).max()))
    plt.title('Histogram - Quality (%)')
    plt.ylabel("Count")
    plt.subplot(3, 1, 2)
    plt.hist(hist_nb_ex, bins=np.arange(np.array(hist_nb_ex).min(), np.array(hist_nb_ex).max()))
    plt.title('Histogram - NB FS examples')
    plt.ylabel("Count")
    plt.subplot(3, 1, 3)
    plt.hist(hist_fs_access, bins=np.arange(np.array(hist_fs_access).min(), np.array(hist_fs_access).max()))
    plt.title('Histogram - FS acess (%)')
    plt.ylabel("Count")
    plt.show()

workbook = xlsxwriter.Workbook('easy_categories.xlsx')
worksheet = workbook.add_worksheet('list categories ACCEPTED')

ontology = json.load(open('ontology_preCrowd.json','rb'))
ontology_by_id = {o['id']:o for o in ontology}

all_categories_with_stats = json.load(open('node_quality_nbExamples_fsAccess.json','rb'))
remaining_categories = [s for s in all_categories_with_stats if all_categories_with_stats[s][0]>MIN_QUALITY and all_categories_with_stats[s][1]>MIN_EXAMPLES and all_categories_with_stats[s][2]<MAX_ACCESSS_FS]

filtered_categories = [s for s in all_categories_with_stats if s not in remaining_categories]

all_categories = remaining_categories + filtered_categories

categories = []
for node_id in all_categories:
    paths = [o for o in get_all_parents(node_id, ontology)]
    l = paths[0] + [ontology_by_id[node_id]["name"]]
    if node_id in remaining_categories:
        if len(paths) < 2:
            categories.append((' > '.join(l), node_id, 'ACCEPTED'))       
        else:
            categories.append((' > '.join(l) + '  // MULTIPLE PARENTS', node_id, 'ACCEPTED'))
     
categories = sorted(categories, key=lambda a: a[0])

for idx, obj in enumerate(categories):
    worksheet.write(idx, 0, obj[0])
    worksheet.write(idx, 1, obj[1])

worksheet2 = workbook.add_worksheet('list categories ALL')
categories = []
for node_id in all_categories:
    paths = [o for o in get_all_parents(node_id, ontology)]
    l = paths[0] + [ontology_by_id[node_id]["name"]]
    if node_id in remaining_categories:
        if len(paths) < 2:
            categories.append((' > '.join(l), node_id, 'ACCEPTED'))       
        else:
            categories.append((' > '.join(l) + '  // MULTIPLE PARENTS', node_id, 'ACCEPTED'))
    else:
        if len(paths) < 2:
            categories.append((' > '.join(l), node_id, 'REMOVED'))       
        else:
            categories.append((' > '.join(l) + '  // MULTIPLE PARENTS', node_id, 'REMOVED'))

categories = sorted(categories, key=lambda a: a[0])

for idx, obj in enumerate(categories):
    worksheet2.write(idx, 0, obj[0])
    worksheet2.write(idx, 1, obj[1])
    worksheet2.write(idx, 2, obj[2])

workbook.close()

plot_histograms(all_categories_with_stats)

