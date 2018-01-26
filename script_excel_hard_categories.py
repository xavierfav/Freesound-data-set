import json
import xlsxwriter

BASE_URL = 'https://datasets.freesound.org/fsd/annotate/'

workbook = xlsxwriter.Workbook('hard_categories.xlsx')
worksheet = workbook.add_worksheet('Hyperlinks')
url_format = workbook.add_format({
    'font_color': 'blue',
    'underline':  0
})

categories_dict = json.load(open('hard_categories.json', 'rb'))
id_url = json.load(open('id_url.json', 'rb'))

for key, value in id_url.iteritems():
    id_url[key] = value.split('/contribute/')[1]

categories = sorted([(key, value[0], value[1]) for key, value in categories_dict.iteritems()], key=lambda x:x[1])
coordinates = ['A'+str(1+x) for x in range(len(categories))]

for idx, category in enumerate(categories):
    if len(category[1]) > 1:
        worksheet.write_url(coordinates[idx], BASE_URL+id_url[category[0]], url_format, str(category[1][0]+' (many parents)'))
    else:
        worksheet.write_url(coordinates[idx], BASE_URL+id_url[category[0]], url_format, str(category[1][0]))
workbook.close()

