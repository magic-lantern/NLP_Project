import nltk.data
from nltk.corpus import wordnet
from nltk.tokenize import word_tokenize
from nltk import pos_tag
from nltk.wsd import lesk
import random

# Brief info on what you can do with wordnet in NLTK
# http://www.nltk.org/howto/wordnet.html

# this one treats the list of synonyms as a set and returns a random synonym
def synonym_picker(word, pos):
    synonyms = set()
    for syn in wordnet.synsets(word, pos=pos):
        for l in syn.lemmas():
            synonyms.add(l.name().replace('_', ' '))
    #print('    ', synonyms)
    if len(synonyms) > 0:
        #print('    random selection: ', random.choice(list(synonyms)))
        return random.choice(list(synonyms))
    else:
        return word

# this one keeps the list of synonyms in order and returns the first one
# seems to make more sense than the random set based option
def synonym_picker2(word, pos):
    synonyms = []
    for syn in wordnet.synsets(word, pos=pos):
        for l in syn.lemmas():
            if l.name() not in synonyms and l.name() != word:
                synonyms.append(l.name().replace('_', ' '))
    if len(synonyms) > 0:
        return synonyms[0]
    else:
        return word

# other idea:
# keeps the list of synonyms in order and returns the one with the highest symantic
# similarity. For details on possible methods for calculating,
# see
#   http://www.sersc.org/journals/IJHIT/vol6_no1_2013/1.pdf
#   http://www.nltk.org/howto/wsd.html
#   word.res_similarity(synset2, ic)
#   word.jcn_similarity(synset2, ic)
#   word.lin_similarity(synset2, ic)
# first determine word sense using Lesk word sense disambiguation
# then find synonyms
#
# PROBLEM: New word doesn't have the correct tense (if anything other then default present tense)
#          it appears that the Python 2 only library "Pattern" would solve this...
# PROBLEM: This process doesn't take into account singluar vs plural nouns
#
def synonym_picker3(word, wpos, sentence, npos):
    #print(word, pos, sentence)
    #print(word, " ", npos)
    start_synset = lesk(sentence, word, wpos)
    synonyms = []
    #start_synset.res_similarity()
    if (start_synset):
        #print(start_synset.lemmas())
        for l in start_synset.lemmas():
            if l.name() not in synonyms and l.name() != word:
                synonyms.append(l.name().replace('_', ' '))
        if len(synonyms) > 0:
            return random.choice(list(synonyms))
        else:
            return word
    else:
        return word


if __name__ == "__main__":
    # to get a list of all possible tags
    #print(nltk.help.upenn_tagset())

    sampletext = '''
Charlene,

So you now have education content on all whiteboards (someone will first have to first do a clear all to see it). As you know, 2147 is using the whiteboard for sound, and as we discussed in the meeting, we added a USB speaker to 2146.

We have a wireless speaker option that we tested in 2143, but as we don't yet have a mounting bracket finished, did not leave the speaker. We should have that completed soon and can then figure out where a preferred mounting location would be.

If you or anyone tests out the education videos, please let us know your thoughts on the volume as well as how loud it is from the hall as well as adjacent rooms. We're particularly concerned with 2146 being loud in 2147 as the speaker for 2146 is behind the whiteboard.

Seth
'''

    # general logic
    # for each word, determine if it is a noun or a verb
    # find synonyms for word
    # output random synonym for word

    sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
    tokenized = sent_detector.tokenize(sampletext.strip())

    for i in tokenized:
        words = word_tokenize(i)
        tagged = pos_tag(words)
        madlib = []
        for t in tagged:
            #print(t)
            if t[1][:2] == 'VB':
                #madlib.append(synonym_picker2(t[0], wordnet.VERB))
                madlib.append(synonym_picker3(t[0], wordnet.VERB, words, t[1]))
            elif t[1][:2] == 'NN':
                #madlib.append(synonym_picker2(t[0], wordnet.NOUN))
                madlib.append(synonym_picker3(t[0], wordnet.NOUN, words, t[1]))
            elif t[1][:2] == 'JJ':
                #madlib.append(synonym_picker2(t[0], wordnet.ADJ))
                madlib.append(synonym_picker3(t[0], wordnet.ADJ, words, t[1]))
            elif t[1][:2] == 'RB':
                #madlib.append(synonym_picker2(t[0], wordnet.ADV))
                madlib.append(synonym_picker3(t[0], wordnet.ADV, words, t[1]))
            else:
                madlib.append(t[0])
        n = ''
        p = ''
        for i, m in enumerate(madlib):
            if i < len(madlib) - 1:
                n = madlib[i+1]
            if i > 0:
                p = madlib[i-1]
            #print('p: ', p)
            #print('m: ', m)
            #print('n: ', n)
            if n == ',' or n == '.' or n == ')' or m == '(':
                print(m, end="")
            else:
                print(m, end=" ")
        print()
