import random
import sqlite3
import os
from nltk.corpus import stopwords
import re
from collections import Counter

def get_documents():
    # documents - convert some sentences to a bag of words!
    # these 'documents' are selected from the MIMICIII dataset
    # number of n for word ngrams to build

    sqlitedb = os.path.join(os.path.expanduser('~'),'Box Sync', 'GradSchoolStuff', 'MastersProject', 'mimic3', 'mimic3.sqlite')
    if not (os.path.exists(sqlitedb)):
        print("Specified database does not exist")
        sys.exit()

    # with is supposed to close automatically if there is an error
    connection = sqlite3.connect(sqlitedb)

    with connection:
        cur = connection.cursor()
        cur.execute("""
            SELECT text FROM noteevents
            WHERE category = 'Radiology' AND
              text LIKE '%pulmonary embolism%' AND
              _ROWID_ >= (abs(random()) % (SELECT max(_ROWID_) FROM noteevents))
            LIMIT 10""")
        rows = cur.fetchall()

        if (len(rows) < 10):
            print("Didn't get data, trying again")
            return get_documents()
        else:
            documents = []
            stops = set(stopwords.words("english"))

            for idx, row in enumerate(rows):
                document = []

                # need to clean up each row, remove stop words, tokenize
                text_only = re.sub("[^a-zA-Z]", " ", row[0])
                for w in text_only.split():
                    if w not in stops:
                        document.append(w.lower())
                documents.append(document)

            return documents


# pretty much everything from here down comes from my reading of Data Science from Scratch
# code available at
# https://github.com/joelgrus/data-science-from-scratch/blob/master/code-python3/natural_language_processing.py

# smoothing variables
ALPHA = 0.1
BETA = 0.1

# code from data science from scratch
def sample_from(weights):
    total = sum(weights)

    # create a uniform distribution be 0 and total
    rnd = total * random.random()

    # return the smallest i such that weights[0] + ... + weights[i] >= rnd
    for i, w in enumerate(weights):
        rnd -= w
        if rnd <= 0:
            return i

# the fraction of words in document _d_ that are assigned to _topic_ (plus some smoothing)
def p_topic_given_document(topic, d, alpha=ALPHA):
    return((document_topic_counts[d][topic] + alpha) /
           (document_lengths[d] + K * alpha))

# the fraction of words assigned to _topic_ that equal _word_ (plus some smoothing)
def p_word_given_topic(word, topic, beta=BETA):
    return ((topic_word_counts[topic][word] + beta) /
            (topic_counts[topic] + W * beta))

#given a document and a word in that document, return the weight for the kth topic
def topic_weight(d, word, k):
    return p_word_given_topic(word, k) * p_topic_given_document(k, d)

def choose_new_topic(d, word):
    return sample_from([topic_weight(d, word, k)
                       for k in range(K)])

if __name__ == '__main__':
    # topics to find
    K = 4
    documents = get_documents()
    document_topic_counts = [Counter() for _ in documents]
    topic_word_counts = [Counter() for _ in range(K)]
    topic_counts = [0 for _ in range(K)]
    document_lengths = list(map(len, documents))

    # count the number of distinct words
    distinct_words = set(word for document in documents for word in document)
    W = len(distinct_words)
    D = len(documents)

    random.seed(0)
    document_topics = [[random.randrange(K) for word in document]
                       for document in documents]

    for d in range(D):
        for word, topic in zip(documents[d], document_topics[d]):
            document_topic_counts[d][topic] += 1
            topic_word_counts[topic][word] += 1
            topic_counts[topic] += 1

    for iter in range(100):
        for d in range(D):
            for i, (word, topic) in enumerate(zip(documents[d], document_topics[d])):
                document_topic_counts[d][topic] -= 1
                topic_word_counts[topic][word] -= 1
                topic_counts[topic] -= 1
                document_lengths[d] -= 1

                # choose a new topic based on weights
                new_topic = choose_new_topic(d, word)
                document_topics[d][i] = new_topic

                # now add back to counts
                document_topic_counts[d][new_topic] += 1
                topic_word_counts[new_topic][word] += 1
                topic_counts[new_topic] += 1
                document_lengths[d] += 1

    for k, word_counts in enumerate(topic_word_counts):
        for word, count in word_counts.most_common():
            if count > 0: print(k, word, count)

    topic_names = ["first topic",
               "second topic",
               "third topic",
               "fourth topic"]

    for document, topic_counts in zip(documents, document_topic_counts):
        print(document)
        for topic, count in topic_counts.most_common():
            if count > 0:
                print(topic_names[topic], count)
        print()