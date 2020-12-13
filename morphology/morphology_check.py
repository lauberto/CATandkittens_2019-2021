import mysql.connector
import pandas as pd
import os
import tempfile
import re
import time
from random import randint, uniform
from conllu import parse, parse_tree

from string import punctuation
punctuation += '«»—…“”–•'
punctuation = set(punctuation)
from nltk.corpus import stopwords
stops = stopwords.words('russian')

numbers = re.compile("[0-9]")
latins = re.compile(r"([a-zA-Z]+\W+)|(\W+[a-zA-Z]+)|(\W+[a-zA-Z]\W+)|([a-zA-Z]+)")
cyrillic = re.compile(r"([а-яА-ЯёЁ]+\W+)|(\W+[а-яА-ЯёЁ]+)|(\W+[а-яА-ЯёЁ]\W+)")
initial = re.compile(r"[а-яА-ЯёЁ]\.")

con = mysql.connector.connect(user='andrea',
                              password='rstq!2Ro',
                              host='127.0.0.1',
                              database='cat',
                              auth_plugin='mysql_native_password'
                             )

# cur = con.cursor(dictionary=True, buffered=True) 


class Tagset:
    def __init__(self, unigram, lemm, morph, pos):
        self.unigram = unigram
        self.lemm = lemm
        self.morph = morph
        self.pos = pos

    def morph_to_string(self):
        if self.morph:
            subtaglist = list()
            for tag_element in list(self.morph.items()):
                subtag = '{}={}|'.format(tag_element[0], tag_element[1])
                subtaglist.append(subtag)

            fulltag = ''.join([str(x) for x in subtaglist])
            morph_string = fulltag[:-1]
            return morph_string
        else:
            morph_string = 'None'
            return morph_string


def parser(filename):
    """
    Yields a sentence from conllu tree with its tags

    """
    """
    >>> for i in parser('/content/gdrive/My Drive/Новые conll по доменам/NewVers/CleanedPsyEdu.conllu'):
      print(i)   
    TokenList<Музыка, звучит, отовсюду, независимо, от, нашего, желания, или, нежелания, слушать, ее, .>
    """
    with open(filename, 'r', encoding='utf-8') as f:
        data = f.read()
    tree = parse(data)
    for token in tree:
        yield token


def get_words(tree):
    """
    tree - generator of sentences (TokenLists) from conllu tree

    words, list is a list of all tokens we need from the tree
    size, int is a number of all words in the domain
    """
    words = []
    for sentence in tree:
        for token in sentence:
            if token['form'] != '_' and token['upostag'] != '_' and token['upostag']!='NONLEX' and token['form'] not in r'[]\/':
                for unigram in token['form'].split(): # .lower()
                    words.append((unigram, token['lemma'], token['feats'], token['upostag']))
    size = len(words)
    return words, size

def tagset_lemma(words):
    """
    Expands OrderedDict object to string
    words: list of tuples (unigram, lemm, morph, pos)
    """
    print('tagset being created...')
    word_list = list()
    for word in words:
        tagset = Tagset(*word)
        tagset.morph = tagset.morph_to_string()
        tagset = (tagset.unigram, tagset.lemm, tagset.morph, tagset.pos)
        word_list.append(tagset)
    return word_list


def morph_error_catcher(words):
    mistakes = {}
    corrects = {}
    cur = con.cursor(dictionary=True, buffered=True)
    for i, word in enumerate(words):
        time.sleep(uniform(0.2, 0.6))

        cur.execute("""SELECT unigram, lemm, morph, pos FROM
                    (SELECT unigram, morph, lemma FROM unigrams) AS a JOIN
                    (SELECT id_lemmas, id_pos, lemma AS lemm FROM lemmas) AS b ON lemma = id_lemmas JOIN pos ON b.id_pos = pos.id_pos
                    WHERE unigram="{}" &&
                    lemm="{}" &&
                    morph="{}" &&
                    pos="{}";""".format(word[0], word[1], word[2], word[3]))

        rows = cur.fetchall()
        if not rows:
            mistakes[i] = [word[0], word[1], word[2], word[3]]
        else:
            corrects[i] = [word[0], word[1], word[2], word[3]]
    # print(mistakes, "\n\n", corrects, "\n\n")
    return mistakes, corrects


def correction(filepath, corrected_files_directory):
    '''
    filepath: path to conllu format file
    corrected_files_directory: directory path where the corrected txt file should end up
    '''
    
    filename = os.path.basename(os.path.normpath(filepath))
    # tagset creation
    tree = parser(filepath)
    words, size = get_words(tree)
    del tree   
    
    tot=0
    mists=0
    tagset = tagset_lemma(words)
    correction = []
    mistakes = morph_error_catcher(tagset)[0]
    for i, word in enumerate(tagset):
        if i in mistakes and word[0].lower() not in punctuation and word[0].lower() not in stops and \
        not numbers.match(word[0].lower()) and \
        not latins.search(word[0].lower()) and not cyrillic.search(word[0].lower()) and word[3] != 'PROPN':
            correction.append('++'+word[0]+'++')
            mists+=1
            tot+=1
        else:
            correction.append(word[0])
            tot+=1
    correction = ' '.join(correction)
    os.makedirs(corrected_files_directory, exist_ok=True)
    with open(os.path.join(corrected_files_directory, filename[:-6]+'txt'), 'w', encoding='utf-8') as fw:
        fw.write(correction)
    return print(correction, "\n\nCorrected words: %s" %mists, "\nMistake frequency: %s" %(mists/tot))

def main():
    print("Correcting text prs_EC12_B1_2421.conllu")
    correction(os.path.join(LOW_PRSD, 'prs_EC12_B1_2421.conllu'), CORR_DIR)

    # print("Correcting text prs_EC12-B1-0404.conllu")
    # correction(os.path.join(LOW_PRSD, 'prs_EC12_B1_2421.conllu'), CORR_DIR)

    # print("Correcting text prs_EC12_B1_2421.conllu")
    # correction(os.path.join(REG_PRSD, 'prs_EC12_B1_2421.conllu'), CORR_DIR)

    # print("Correcting text prs_EC12-B1-0732.conllu")
    # correction(os.path.join(REG_PRSD, 'prs_EC12-B1-0732.conllu'), CORR_DIR)

    # print("Correcting text prs_EC12-B1-0732.conllu")
    # correction(os.path.join(MA_THESES, 'prs_EC12-B1-0732.conllu'), CORR_DIR)

    # print("Correcting text prs_EC12-B1-0732.conllu")
    # correction(os.path.join(MA_THESES, 'prs_EC12-B1-0732.conllu'), CORR_DIR)

if __name__ == "__main__":
    main()
                  