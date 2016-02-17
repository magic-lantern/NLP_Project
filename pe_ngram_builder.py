#
# This is an word ngram building that ignores sentence boundaries.
# It pulls data from the CTPA.sqlite database
#

import sqlite3
import os
from nltk.util import ngrams
from nltk.probability import FreqDist
import re

# number of n for word ngrams to build
n = 5
report_col = 4
text = ''

sqlitedb = os.path.join(os.path.expanduser('~'),'Box Sync', 'GradSchoolStuff', 'MastersProject', 'ctpa.sqlite')
if not (os.path.exists(sqlitedb)):
    print("Specified database does not exist")
    sys.exit()

# with is supposed to close automatically if there is an error
connection = sqlite3.connect(sqlitedb)

with connection:
    cur = connection.cursor()
    cur.execute('select count(*) from reports')
    data = cur.fetchall()
    print('Total rows in REPORTS table: ', data[0][0])

    #cur.execute('select * from reports limit 500')
    cur.execute('select * from reports')
    col_names = [cn[0] for cn in cur.description]
    rows = cur.fetchall()

for row in rows:
    text += row[report_col]
#words that should be ignored as they are part of the report structure:
myregexp = '(EXAMINATION PERFORMED:|HISTORY:|CLINICAL HISTORY:|COMPARISON:|TECHNIQUE:|FINDINGS:|IMPRESSION:|END OF IMPRESSION:)'

output = re.sub(myregexp, '', text)
output = output.replace('CT ANGIOGRAPHY CHEST WITH CONTRAST', '')
# clean up new lines, extra spaces
output = re.sub('\n', ' ', output)
output = re.sub('  ', ' ', output)
# remove signature line as that isn't useful
output = output.replace('My signature below is attestation that I have interpreted this/these examination(s) and agree with the findings as noted above.', '')
# remove periods as we're doing a cross sentance boundry ngram
output = re.sub('\.', '', output)
# covert to lower case to find all ngram matches regardless of case
output = output.lower()

# this is a generator object. Once iterate through it, it is empty
grams = ngrams(output.split(), n)

fdist = FreqDist(grams)
#for ng, count in fdist.items():
#    print(ng, count)

for ng,count in fdist.most_common(50):
    print('N-Gram:', ng, 'Count: ', count)