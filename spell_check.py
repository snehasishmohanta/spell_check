import re, collections
import sys
import itertools
from collections import defaultdict
import math


unigramCount = 21877 #queries occurring once
total = 66710678 # total queries
debug = False
debug = True
def word_sub(word):
    if word[-1] == ".":
        word = word[:-1]
    if word.isdigit():
        word = "__digit"
    elif not word.isalpha() and word.isalnum():
        word = "__alnum"
    elif not word.isalnum():
        word = "__special"
    return word

def starting_prob(word):
    # this is probabality of the word starting a sentence
    if word in unigrams:
        count1 = float(unigrams[word])
        p = count1 / float(total)
    else:
        p = 1 / float(8944985) # frequency of space

    word = word_sub(word)
 
    if '^' in bigrams[word] and '$' in bigrams[word] :
        x = bigrams[word]['^']
        y = bigrams[word]['^'] + bigrams[word]['$']
    else:
       #same probabilty as a non seen bigram
       x = 0.00005
       y = 1 + float(total)/unigramCount

    p *= float(x)/float(y)
    return p

def get_end_probability(word):
    word = word_sub(word)
    # this is probabality of the word being the last word in a sentence
    if '^' in bigrams[word] and '$' in bigrams[word] :
        x = bigrams[word]['$'] #+ float(unigramCount)
        y = bigrams[word]['^'] + bigrams[word]['$'] #+ float(unigramCount) + float(total)
    else:
       #same probabilty as a non seen bigram               
       #x = 0.0005
       x = 0.00005
       y = 1 + float(total)/unigramCount

    p = float(x)/float(y)
    return p


def first_alpha(words):
    for word in words:
        if word.isalpha():
            return word
    return None

def calProb(unigrams,bigrams,words):
    #product model
    pWord=word_sub(words[0])
#    print "word:", pWord
#    p = (1.0 + base_dict[pWord]) if pWord in base_dict else 1.0
    first_alpha_word = first_alpha(words)
    if not first_alpha_word:
        return 1
    if debug:
        print "first alpha word: ", first_alpha_word 
    p = starting_prob(first_alpha_word)
#    print words
    if debug:
        print "start:", p
    min_x = 100000
    for i in range(1,len(words)):
        word = word_sub(words[i])
        x = float( bigrams[pWord][word]) + float( bigrams[word][pWord])# + 10.0
        if debug:
            print "joint prob of " + pWord +" "+word + " is: " + str(x)
        joint_prob=True
        if x < 1:
            x = 1 / float(8944985) # frequency of space
            joint_prob = False
        # adding this because if a bigram has not been seen but
        # the next unigram is a valid word (i.e. its freqency is high)
        # give it some weight
            if word in unigrams:
                x *= 1+ math.log(float(unigrams[word]))
        if pWord in unigrams:
            y = float(unigrams[pWord])
        else:
            y = 8944985# - float(unigramCount)/(float(total))
        if debug:
            print "prob of " + pWord + " is: " + str(y)
            print "prob of ", word, "/" + pWord + " :", float(x)/float(y)
        pWord = word       
        p *= float(x)/float(y)
        if float(unigrams[word])<min_x:
            min_x = float(unigrams[word])
    if debug:
        print "min x:", min_x
    p *= float(min_x)/total
    #p *=  get_end_probability(words[-1])
  #  print "end:", get_end_probability(words[-1])
    return p


def read_bigrams():
    bigrams = defaultdict(lambda : defaultdict(int))
    for line in open('validBigrams.txt'):
        line = line.lower().strip()
        data = line.split(':')
        key = data[0]
        rest = ' '.join(data[1:]).split(',\t')
        for val in rest:
            bKey = val.split(',')
            bigrams[key][bKey[0]] = int(bKey[1])
    return bigrams
  
def read_unigrams(): 
    unigrams = {}
    for line in open('validUnigrams.txt'):
        line = line.lower().strip()
        data = line.split(',')
        unigrams[data[0]] = data[1]
    return unigrams

def read_dict():
    d = dict()
    total = 0
    for line in open("base_dict.txt", "r"):
        q, f = line.strip().split(',')
        d[q] = int(f)
        total += int(f)
    for k, v in d.iteritems():
        d[k] = float(v)/total
    print "total", total
    return d

def words(text): return re.findall('[a-z]+', text.lower()) 

def train(f):
    model = collections.defaultdict(lambda: 1)
    for line in open(f, "r"):    
        w, f = line.split(',')
        model[w] += int(f)
    return model

NWORDS = train('base_dict.txt')

alphabet = 'abcdefghijklmnopqrstuvwxyz'

def edits1(word):
   splits     = [(word[:i], word[i:]) for i in range(len(word) + 1)]
   deletes    = [a + b[1:] for a, b in splits if b]
   transposes = [a + b[1] + b[0] + b[2:] for a, b in splits if len(b)>1]
   replaces   = [a + c + b[1:] for a, b in splits for c in alphabet if b]
   inserts    = [a + c + b     for a, b in splits for c in alphabet]
   return list(deletes + transposes + replaces + inserts)

def known_edits2(word):
    return list(e2 for e1 in edits1(word) for e2 in edits1(e1) if e2 in NWORDS)

def known(words): return list(w for w in words if w in NWORDS)

def get_combo(list_of_lists):
    combinations = list(set(list(itertools.product(*list_of_lists))))
    return combinations

def generateCandidates(unigram):

    candidate = set()

    alphabets = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']

    if unigram in unigrams:
        candidate.add(unigram)

    for i in xrange(0,len(unigram)+1):
        key = unigram[0:i] +  unigram[i+1:]
        if key in unigrams:
            candidate.add(key)

        if i >= len(unigram):
            continue
        alphabet = unigram[i]
        for j in xrange(0,len(key)+1):
            transpose = key[0:j] + alphabet + key[j:]
            #print transpose
            if transpose in unigrams:
                candidate.add(transpose)

    for alphabet in alphabets:
        for i in xrange(0,len(unigram)+1):
            key = unigram[0:i] + alphabet + unigram[i:]
            #print key
            if key in unigrams:
                #print key,unigrams[key]
                candidate.add(key)
            if key+'s' in unigrams:
                candidate.add(key+'s')
            key = unigram[0:i] + alphabet+alphabet + unigram[i:]
            #print key
            if key in unigrams:
                #print key,unigrams[key]
                candidate.add(key)

    for i in xrange(0,len(unigram)+1):
        key = unigram[0:i] +  unigram[i+1:]
        for alphabet in alphabets:
            for i in xrange(0,len(key)+1):
                newKey = key[0:i] + alphabet + key[i:]
                if newKey in unigrams:              
                    candidate.add(newKey)
    return candidate

def read_bigrams_old():
    bigrams = collections.defaultdict(lambda:0)
    for line in open("unigram_prob", "r"):
        bigram, freq = line.strip().split('\t')
        bigrams[bigram] = float(freq)
    return bigrams

bigrams = read_bigrams()
unigrams = read_unigrams()
base_dict = read_dict()

for line in open(sys.argv[1], "r"):
    all_candidates = list()
    words = line.strip().split()
    for word in words:
        if word.isalpha():
            candidates = list(set(known([word]) + known(edits1(word)) + [word]))
        else:
            candidates = [word]
        all_candidates.append(candidates)
    total_c = 1
    for c in all_candidates:
        total_c *= len(c)
    if total_c > 10000:
        continue
    combos = get_combo(all_candidates)
    d = dict()
    for combo in combos:
        if " ".join(combo) == line.strip() or " ".join(combo) == "ng nov dumbells" or " ".join(combo) == "dumbells nov ng":
            if debug:
                print combo
            d[" ".join(combo)] = calProb(unigrams, bigrams, combo)
            if debug:
                print "final prob: ", d[" ".join(combo)]
    if debug:
        for k in sorted(d, key=d.get, reverse=True):
            print k + "\t" + str(d[k])
#    d.pop(max(d, key=lambda x: d[x]))
    recommended = max(d, key=lambda x: d[x]) if len(d.keys())>1 else line.strip()
    if recommended != line.strip():
        print line.strip() +">>>>"+ recommended + "\t" +str(d[recommended])

