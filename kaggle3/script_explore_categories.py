import json
import webbrowser


def create_html_with_examples(ex_candidates, aso_id):
    """
    Create a html page with FS sound embeds
    Arguments   - ex_candidates:    dict with <aso_id> : [<list_fs_id>]
                - aso_id:           category id from ASO
    """
    
    try:
        sounds = ex_candidates[aso_id]
    except:
        print '%s This category does not exist (it has not been voted)'% (aso_id,)
        return
    
    # This list contains the begining and the end of the embed
    # Need to insert the id of the sound
    embed_blocks = ['<iframe frameborder="0" scrolling="no" src="https://www.freesound.org/embed/sound/iframe/', '/simple/medium/" width="481" height="86"></iframe>']
    # Create the html string
    message = """
    <html>
        <head></head>
        <body>
    """
    for idx in sounds:
        message += str(idx) + embed_blocks[0] + str(idx) + embed_blocks[1] + "<br/>"
    message += """
        </body>
    </html>
    """
    
    # Create the file
    f = open('category_'+ str(ontology_by_id[aso_id]['name']) +'.html', 'w')
    f.write(message)
    f.close()
    # Open it im the browser
    webbrowser.open('category_'+ str(ontology_by_id[aso_id]['name']) +'.html')
    

if __name__ == '__main__':
    """   
    From the terminal in the Freesound-data-set/kaggle3 folder, type:
    >>> python script_explore_categories.py
    
    You will be asked for the category you want to deal with. Enter the id of the category.
    
    An html page will be generated and oppened with the examples candidates.
    
    The page will present a sound in each line with the freesound embed to be able to listen to it.
    """

    data_eval = json.load(open('json/data_eval.json','rb'))
    data_dev_HQ = json.load(open('json/data_dev_HQ.json', 'rb'))
    ontology = json.load(open('json/ontology.json','rb'))
    ontology_by_id = {o['id']:o for o in ontology}
    dev_or_eval = raw_input('Explore dataset dev HQ or eval set (type dev/eval): ')
    if dev_or_eval == 'dev':
        data = data_dev_HQ
    elif dev_or_eval == 'eval':
        data = data_eval
    aso_id = raw_input('Enter the id of the category you want to deal with (without quotes): ')
    create_html_with_examples(data, aso_id)
    