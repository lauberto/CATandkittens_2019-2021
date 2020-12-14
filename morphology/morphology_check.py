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

class Tagset:
    def __init__(self, unigram, lemm, morph, pos, start_id, end_id):
        self.unigram = unigram
        self.lemm = lemm
        self.morph = morph
        self.pos = pos
        self.start_id = start_id
        self.end_id = end_id

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
    
    def to_dict(self):
        return dict([('unigram', self.unigram), ('lemm', self.lemm), ('morph', self.morph), \
            ('pos', self.pos), ('start_id', self.start_id), ('end_id', self.end_id)])

# TODO: combine funcitons "add_ids" and "get_words" 

def add_ids(conllu_sents, text, prev_text_len=0):
    text_copy = text
    for sent in conllu_sents:
        for token in sent.tokens:
            form = token['form']
            position = text_copy.find(form)
            token['start_id'] = prev_text_len + position
            token['end_id'] = prev_text_len + position + len(form)
            text_copy = text[position+len(form):]
            prev_text_len = prev_text_len+position+len(form)
    for token in conllu_sents:
        yield token
    # return conllu_sents

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


def get_words(tree, txtfile, prev_text_len=0):
    """
    tree - generator of sentences (TokenLists) from conllu tree
    txtfile - txt version of the conllu file

    words, list is a list of all tokens we need from the tree
    size, int is a number of all words in the domain
    """
    with open(txtfile, 'r', encoding='utf-8') as f:
        text = f.read() 
    text_copy = text
    words = []
    for sentence in tree:
        for token in sentence:
            form = token['form']
            position = text_copy.find(form)
            token['start_id'] = prev_text_len + position
            token['end_id'] = prev_text_len + position + len(form)
            text_copy = text[position + len(form):]
            prev_text_len = prev_text_len + position + len(form)
            if token['form'] != '_' and token['upostag'] != '_' and token['upostag']!='NONLEX' and token['form'] not in r'[]\/':
                for unigram in token['form'].split(): # .lower()
                    words.append((unigram, token['lemma'], token['feats'], token['upostag'],
                    token['start_id'], token['end_id']))
    size = len(words)
    return words, size

def tagset_lemma(words):
    """
    Expands OrderedDict object to string
    words: list of tuples (unigram, lemm, morph, pos, start_id, end_id)
    """
    print('tagset being created...')
    word_list = list()
    for word in words:
        tagset = Tagset(*word)
        tagset.morph = tagset.morph_to_string()
        tagset = tagset.to_dict()
        word_list.append(tagset)
    return word_list


def morph_error_catcher(words):
    mistakes = {}
    corrects = {}
    cur = con.cursor(dictionary=True, buffered=True)
    for i, word in enumerate(words):
        if word['unigram'].lower() not in punctuation and word['unigram'].lower() not in stops and \
        not numbers.match(word['unigram'].lower()) and not latins.search(word['unigram'].lower()) and \
        not cyrillic.search(word['unigram'].lower()) and word['pos'] != 'PROPN':

            time.sleep(uniform(0.2, 0.6))

            cur.execute("""SELECT unigram, lemm, morph, pos FROM
                        (SELECT unigram, morph, lemma FROM unigrams) AS a JOIN
                        (SELECT id_lemmas, id_pos, lemma AS lemm FROM lemmas) AS b ON lemma = id_lemmas JOIN pos ON b.id_pos = pos.id_pos
                        WHERE unigram="{}" &&
                        lemm="{}" &&
                        morph="{}" &&
                        pos="{}";""".format(word['unigram'], word['lemm'], word['morph'], word['pos']))

            rows = cur.fetchall()
            if not rows:
                mistakes[i] = word
            else:
                corrects[i] = word
    # print(mistakes, "\n\n", corrects, "\n\n")
    return mistakes, corrects


def correction(filepath, filetxt, corrected_files_directory, print_correction=False):
    '''
    filepath: path to conllu format file
    filetxt: txt version of the same file
    corrected_files_directory: directory path where the corrected txt file should end up
    print_correction = flag in to get a txt file with correction in the destination directory
    '''

    filename = os.path.basename(os.path.normpath(filepath))
    # tagset creation
    tree = parser(filepath)
    words, _ = get_words(tree, filetxt)
    del tree   
    
    tot=0
    mists=0
    tagset = tagset_lemma(words)
    # words_ids = []
    mistakes, _ = morph_error_catcher(tagset)
    mistakes_list = mistakes.values()

    if print_correction == True:

        correction = list()
        for i, word in enumerate(tagset):
            if i in mistakes:
                correction.append('++'+word['unigram']+'++')
                mists+=1
                tot+=1
            else:
                correction.append(word['unigram'])
                tot+=1
        correction = ' '.join(correction)
    
        os.makedirs(corrected_files_directory, exist_ok=True)
        with open(os.path.join(corrected_files_directory, filename[:-6]+'txt'), 'w', encoding='utf-8') as fw:
            fw.write(correction)
        print(correction, "\n\nCorrected words: %s" %mists, "\nMistake frequency: %s" %(mists/tot))

    return mistakes_list

def main():
    # mistakes_indices = correction(test_conllu, test_txt, CORR_DIR, False)
    # print(mistakes_indices)

if __name__ == "__main__":
    main()