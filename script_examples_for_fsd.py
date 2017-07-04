import json
import webbrowser

def create_html_with_examples(ex_candidates, aso_id, nb_sounds=20):
    """
    Create a html page with FS sound embeds
    Arguments   - ex_candidates:    dict from the file examples_fsd.json
                - aso_id:           category id from ASO
                - nb_sounds:        number of sound to add in the html file
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
    for idx in sounds[:nb_sounds]:
        message += str(idx) + embed_blocks[0] + str(idx) + embed_blocks[1]
    message += """
        </body>
    </html>
    """
    
    # Create the file
    f = open('category_'+ str(ontology_by_id[aso_id]['name']) +'.html', 'w')
    f.write(message)
    f.close()
    # Open it im the browser
    webbrowser.open_new_tab('category_'+ str(ontology_by_id[aso_id]['name']) +'.html')
    

if __name__ == '__main__':
    ex_candidates = json.load(open('examples_fsd.json','rb'))
    ontology = json.load(open('ontology_preCrowd.json','rb'))
    ontology_by_id = {o['id']:o for o in ontology}
    aso_id = raw_input('Enter the id of the category you want to deal with (without quotes): ')
    create_html_with_examples(ex_candidates, aso_id)