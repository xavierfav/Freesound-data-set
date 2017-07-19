import pickle
import json
import xlsxwriter


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


workbook = xlsxwriter.Workbook('examples_FS.xlsx')
worksheet = workbook.add_worksheet('list categories')

ontology = json.load(open('ontology_preCrowd.json','rb'))
ontology_by_id = {o['id']:o for o in ontology}
categories = []
for idx, key in enumerate(ontology_by_id.keys()):
    if not 'omittedTT' in ontology_by_id[key]['restrictions']:
        paths = [o for o in get_all_parents(key, ontology)]
        l = paths[0] + [ontology_by_id[key]["name"]]
        if len(paths) < 2:
            categories.append((' > '.join(l), key))       
        else:
            categories.append((' > '.join(l) + '  // MULTIPLE PARENTS', key))       
        
categories = sorted(categories, key=lambda a: a[0])

for idx, obj in enumerate(categories):
    worksheet.write(idx, 0, obj[0])
    worksheet.write(idx, 1, obj[1])

workbook.close()


