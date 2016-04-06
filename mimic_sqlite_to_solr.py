import sqlite3
import os
import pysolr
import re
import sys

sqlitedb = os.path.join(os.path.expanduser('~'), 'Box Sync', 'GradSchoolStuff',
                        'MastersProject', 'mimic3', 'mimic3.sqlite')
if not (os.path.exists(sqlitedb)):
    print("Specified database does not exist")
    sys.exit()

connection = sqlite3.connect(sqlitedb)

# Connect to Solr instance.
solr = pysolr.Solr('http://192.168.99.100:8983/solr/radiology')

with connection:
    cur = connection.cursor()
    recordset = cur.execute("""
        SELECT * FROM noteevents
        WHERE description LIKE '%CT%'
            AND description NOT LIKE '%ERECT%'
            AND description NOT LIKE '%PLCT%'
            AND category = 'Radiology'
        ORDER BY row_id""")
    col_names = [cn[0] for cn in cur.description]

    # general match for section start
    #section_re = re.compile('^\s+([A-Z]+\s*){2,}:*')
    section_re = re.compile('^\s+([A-Z]+\s*){2,}(:|$)+')

    # patterns for reason section
    reason_1 = re.compile('^\s*REASON FOR THIS EXAMINATION:\s*$')
    reason_2 = re.compile('^\s*Reason:')

    # patterns for the impression section
    impression_1 = re.compile('.*(IMPRESSION|IMPRSSION|IMPRESSON|IMRESSION|Impression)(s:|S:|;|:|$)*')
    impression_2 = re.compile('^\s*(OVERALL)?\s*CONCLUSION[S]?[:]?')
    impression_3 = re.compile('^\s*S(UMMARY|ummary):?\s*')

    # pattern for findings section - only using this if none of the above impression
    # sections matched
    finding_1 = re.compile('.*\sFINDING(S)?(:)?')
    finding_2 = re.compile('.*\sPFI(:)?(\sREPORT)?')

    missing_count = 0
    found_count = 0
    total_count = 0
    finding_count = 0

    for row in recordset:
        document = {}
        #print('++++++', col_names[idx], ': ', col)
        # want row_id, subject_id, hadm_id, description, text
        document['id'] = row[col_names.index("ROW_ID")]
        document['SUBJECT_ID_i'] = row[col_names.index("SUBJECT_ID")]
        # not all reports have a hospital admission id, so this may not be in Solr
        document['HADM_ID_i'] = row[col_names.index("HADM_ID")]
        # store description as a single string, but also allow for searching parts
        document['DESCRIPTION_s'] = row[col_names.index("DESCRIPTION")]
        document['DESCRIPTION_t'] = row[col_names.index("DESCRIPTION")]
        document['TEXT_t'] = row[col_names.index("TEXT")]

        """
        Out of 108,896 reports, only 4 don't use 'REASON FOR THIS EXAMINATION:'
        or 'Reason:' for the reason for exam section. By manual inspection, those 4
        reports are not ones related to PE nor PAH.

        Reports can have multiple reason sections. From inspection of the data,
          * ^'Reason:' (if it exists) is just a one line section and is a portion of the
            'REASON FOR THIS EXAMINATION:' section (if it exists)
          * ^'REASON FOR THIS EXAMINATION:' (if it exists) is a multi-line section and the actual
            reason starts on the next line. There are 3 cases where this section was repeated and
            in some of the repeated locations the reason may partially be on the same line.

        """
        reason_short = ''
        reason_long = ''
        if ('REASON FOR THIS EXAMINATION:' in row[col_names.index("TEXT")]
            or 'Reason:' in row[col_names.index("TEXT")]
           ):
            found_multiline = ''
            for line in row[col_names.index("TEXT")].rstrip().split('\n'):
                # multi-line reason section start -------------
                if reason_1.match(line) is not None:
                    found_multiline = True
                # single line reason section -------------
                elif reason_2.match(line) is not None:
                    reason_short = line.replace('Reason:', '').strip()
                # multi-line reason section continuation -------------
                elif found_multiline:
                    # should add to reason_long until end of section
                    if re.match('^\s\s\w*', line) is not None:
                        reason_long += line
                    else:
                        found_multiline = False
            if len(reason_long.strip()) > 0:
                document['REASON_t'] = reason_long.strip()
                #print(row[col_names.index("ROW_ID")], 'reason_long', reason_long.strip())
            else:
                document['REASON_t'] = reason_short
                #print(row[col_names.index("ROW_ID")], 'reason_short', reason_short)
        else:
            print('------------reason missing for', row[col_names.index("ROW_ID")])

        '''
        Identify impression section. Generally starts with 'IMPRESSION:' followed by newline, then text
        found some that have colon on next line...

        Found some have 'CONCLUSION' instead of 'IMPRESSION'

        Some of those that didn't have either IMPRESSION nor CONCLUSION had 'Summary'

        12 out of 500 selected by ordered row_id did not match the above sections - most of those have a
        findings section that appears to cover both the detailed radiological findings and communication
        to physician

        Some documents have a 'PROVISIONAL FINDINGS IMPRESSION (PFI):' section that we want to avoid.

        Found some reports that have 2 impression sections - an original and an updated one. Probably need both

        Some missing IMPRESSION and CONCLUSION, just have FINDINGS section. Some have 'FINDINGS' section
        then FINDINGS again when it should probably be IMPRESSION. Should that be a substitute? Only if
        none of the other 'IMPRESSION' like sections have been found. When looking for FINDINGS section,
        start at bottom and read up.
        '''
        found_impression = False
        found_summary = False
        found_conclusion = False
        found_findings = False
        skip_section = False
        if ('IMPRESSION' in row[col_names.index("TEXT")]
            or 'IMPRSSION' in row[col_names.index("TEXT")]
            or 'IMPRESSON' in row[col_names.index("TEXT")]
            or 'IMRESSION' in row[col_names.index("TEXT")]
            or 'Impression' in row[col_names.index("TEXT")]
            or 'CONCLUSION' in row[col_names.index("TEXT")]
            or 'SUMMARY' in row[col_names.index("TEXT")]
            or 'Summary' in row[col_names.index("TEXT")]
           ):
            found_count += 1
            found_match_per_record = 0
            section = ''
            found_section = False
            for line in row[col_names.index("TEXT")].rstrip().split('\n'):
                # it is possible that there are multiple 'impression' or impression-like sections
                # if there are multiple sections, keep all of them.
                if impression_1.match(line) is not None:
                    found_impression = True
                    found_match_per_record += 1
                    section += impression_1.sub('', line)
                    found_section = True
                    #print(row[col_names.index("ROW_ID")], line)
                    continue

                if impression_2.match(line) is not None:
                    found_conclusion = True
                    found_match_per_record += 1
                    section += impression_2.sub('', line)
                    found_section = True
                    #print(row[col_names.index("ROW_ID")], line)
                    continue

                if impression_3.match(line) is not None:
                    found_summary = True
                    found_match_per_record += 1
                    section += impression_3.sub('', line)
                    found_section = True
                    #print(row[col_names.index("ROW_ID")], line)
                    continue

                # should add to reason_long until end of section
                if found_section:
                    if '(Over)' in line:
                        skip_section = True
                        found_section = False
                    elif section_re.match(line) is None:
                        #print(row[col_names.index("ROW_ID")], 'continuing section: ', line)
                        section += line
                    else:
                        #print(row[col_names.index("ROW_ID")], 'ending section: ', line)
                        found_section = False

                # page breaks are normally wrapped in (Over)...(Cont)
                if skip_section:
                    if '(Cont)' in line:
                        skip_section = False
                        found_section = True

            document['IMPRESSION_t'] = section

            # this section for debugging purposes to look at documents with multiple impression-like
            # sections
            #if ((found_impression and (found_conclusion or found_summary)) or
            #(found_conclusion and (found_impression or found_summary)) or
            #(found_summary and (found_conclusion or found_impression))):
            #    print(row[col_names.index("ROW_ID")], 'has multiple matches.')
            #    print ('    section found:', section)


        ####
        #### need to identify and extract findings section...
        ####

        # Identify Findings section only if no impression like section found
        total_count += 1
        found_findings = False
        found_section = False
        skip_section = False
        section = ''
        if ('IMPRESSION_t' not in document and
            ('FINDING' in row[col_names.index("TEXT")] or
            'PFI' in row[col_names.index("TEXT")])
           ):
            for line in row[col_names.index("TEXT")].rstrip().split('\n'):
                if finding_1.match(line) is not None:
                    found_findings = True
                    section += finding_1.sub('', line)
                    found_section = True
                    #print(row[col_names.index("ROW_ID")], line)
                    continue
                elif finding_2.match(line) is not None:
                    found_findings = True
                    section += finding_2.sub('', line)
                    found_section = True
                    #print(row[col_names.index("ROW_ID")], line)
                    continue

                # should add to finding like section until end of section
                if found_section:
                    if '(Over)' in line:
                        skip_section = True
                        found_section = False
                    elif section_re.match(line) is None:
                        section += line
                    else:
                        found_section = False

                # page breaks are normally wrapped in (Over)...(Cont)
                if skip_section:
                    if '(Cont)' in line:
                        skip_section = False
                        found_section = True

            if found_findings == True:
                if ('IMPRESSION_t' in document):
                    print('THIS SHOULD NOT BE POSSIBLE')
                document['IMPRESSION_t'] = section
                #print(row[col_names.index("ROW_ID")], 'section found:', section )
                finding_count += 1

        elif 'IMPRESSION_t' not in document:
            print(row[col_names.index("ROW_ID")], '------------no impression nor finding sections')
            _ = 1

        if (found_impression == False and
            found_conclusion == False and
            found_summary == False and
            found_findings == False
           ):
            missing_count += 1

    print('Found:', found_count)
    print('No impression but findings: ', finding_count)
    print('Missing:', missing_count)
    print('Total:', total_count)
        #print('Adding row_id', row[col_names.index("ROW_ID")], 'to Solr.')
        #solr.add([document])

print()