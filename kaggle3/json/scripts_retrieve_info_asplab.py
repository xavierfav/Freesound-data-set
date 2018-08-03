



# get all the categories in FSD, all of them
qs = TaxonomyNode.objects.all()

# print all their names
for taxonomy_node in qs:
    print(taxonomy_node.name)

# load FSD:
my_taxo = Taxonomy.objects.first()

# get hierarchy path for every category
hierarchy_dict = {}
for tn in qs:
    hierarchy_dict[tn.node_id]= [[TaxonomyNode.objects.get(node_id=node_id).name for node_id in path_list] for path_list in my_taxo.get_hierarchy_paths(tn.node_id)]


json.dump(hierarchy_dict,
          open('/fsdatasets_releases/hierarchy_dict.json', 'w'))





