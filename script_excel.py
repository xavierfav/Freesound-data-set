import pickle
import json
import xlsxwriter

BASE_URL = 'https://datasets.freesound.org'

workbook = xlsxwriter.Workbook('hyperlink3.xlsx')
worksheet = workbook.add_worksheet('Hyperlinks')
url_format = workbook.add_format({
    'font_color': 'blue',
    'underline':  1
})
votes_TT = pickle.load(open('votes_TT_all.pkl','rb'))
id_url = json.load(open('id_url.json'))


categories = [vote for vote in votes_TT] # here select only the category that you want to get
# for instance, categories = [vote for vote in votes_TT if vote[8]>24] for TT2

coordinates = ['A'+str(1+x) for x in range(len(categories))]

for idx, category in enumerate(categories):
    worksheet.write_url(coordinates[idx], BASE_URL+id_url[category[0]], url_format, str(category[1]))

workbook.close()


