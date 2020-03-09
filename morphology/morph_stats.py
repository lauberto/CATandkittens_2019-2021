import mysql.connector
import csv
import pandas as pd
import os
from conllu import parse, parse_tree
from scipy.stats import ttest_ind

pd.set_option('display.max_columns', 100)
pd.set_option('display.max_rows', 100)
pd.set_option('display.width', 1000)

stud_dir = r'C:\Users\Andrea\Desktop\stud_textVSscie_text\Student_texts_for_experiments\stud_txt'
low_lvl = os.path.join(stud_dir, 'Low Level')
reg_lvl = os.path.join(stud_dir, 'Regular Level')
low_prsd = os.path.join(stud_dir, 'Low Level Parsed')
reg_prsd = os.path.join(stud_dir, 'Regular Level Parsed')

con = mysql.connector.connect(user='andr',
                              password='rstq!2Ro',
                              host='127.0.0.1',
                              database='cat_db',
                              auth_plugin='mysql_native_password'
                             )

cur = con.cursor(dictionary=True, buffered=True)

cur.execute("""SELECT morph, pos, freq_all FROM
(SELECT morph, lemma, freq_all FROM unigrams) AS a JOIN
(SELECT id_lemmas, id_pos FROM lemmas) AS b ON lemma = id_lemmas JOIN pos ON b.id_pos = pos.id_pos;""")

rows = cur.fetchall()
if 'corpus_stats.csv' in os.getcwd():
    os.system('rm -r corpus_stats.csv')

with open('corpus_stats.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['morph', 'POS', 'count'])
    for dictionary in rows:
        writer.writerow([dictionary['morph'], dictionary['pos'], dictionary['freq_all']])

def corpus_statistics(csv_table_for_corpus):
    df_corpus = pd.read_csv(csv_table_for_corpus)
    if csv_table_for_corpus in os.getcwd():
        os.system('rm -r {}'.format(csv_table_for_corpus))
    df_corpus = df_corpus[df_corpus.morph != '_']
    keys = zip(df_corpus['morph'], df_corpus['POS'], df_corpus['count'])
    dictn = {}
    for key in keys:
        if (key[0], key[1]) in dictn:
            dictn[(key[0], key[1])] += key[2]
        else:
            dictn[(key[0], key[1])] = key[2]

    df_corpus = pd.Series(dictn).reset_index()
    df_corpus.columns = ['tagset', 'POS', 'count']
    df_corpus['part_freq'] = df_corpus['count'].apply(lambda x: x / df_corpus['count'].sum(axis=0))

    return df_corpus

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
        # print(token)
            if token['form'] != '_' and token['upostag'] != '_' and token['upostag']!='NONLEX' and token['form'] not in r'[]\/':
                for wordform in token['form'].lower().split():
                    words.append((wordform, token['feats'], token['upostag']))
    size = len(words)
    return words, size

def tagset_extrapolator(words, filename):
    if 'tagset.csv' in os.getcwd():
        os.system('rm -r tagset.csv')
    with open('tagset.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['token', 'tagset', 'POS'])

        for word in words:
            if word[1]:
                tag_lst = []
                for tag in list(word[1].items()):
                    tag = '{}={}|'.format(tag[0], tag[1])
                    tag_lst.append(tag)

                tag_str = ''.join([str(elem) for elem in tag_lst])
                tag_str = tag_str[:-1]

                writer.writerow([word[0], tag_str, word[2]])
            # print(tag_str)
            else:
                tag_str = 'None'
                writer.writerow([word[0], tag_str, word[2]])

    return print('Tagset table for {} was created'.format(filename))

def stud_txt_statistics(csv_table_for_stud_txt):
    df = pd.read_csv(csv_table_for_stud_txt)
    if csv_table_for_stud_txt in os.getcwd():
        os.system('rm -r "{}"'.format(csv_table_for_stud_txt))

    dictn = {}
    keys = zip(df['tagset'], df['POS'])
    for couple in keys:
        if couple in dictn:
            dictn[couple] += 1
        else:
            dictn[couple] = 1
            
    del df
    
    df_stud = pd.Series(dictn).reset_index()
    df_stud.columns = ['tagset', 'POS', 'count']
    df_stud['part_freq'] = df_stud['count'].apply(lambda x: x / df_stud['count'].sum(axis=0))
    
    return df_stud

def stat_dict(df):
    df_kfreq = zip(df['tagset'], df['POS'], df['part_freq'])
    freq_dict = {(elem[0], elem[1]) : (elem[2],) for elem in df_kfreq}
    return freq_dict

def t_test(conll_dir):
    df_corpus = corpus_statistics('corpus_stats.csv')
    if 'corpus_statistics.csv' in os.getcwd():
        os.system('rm -r corpus_statistics.csv')
    corpus_dict = stat_dict(df_corpus)
    ttest_dict = {}

    for txt in os.listdir(conll_dir):
        tree = parser(os.path.join(conll_dir, txt))
        words, size = get_words(tree)
        tagset_extrapolator(words, txt)
        del tree
        df_stud = stud_txt_statistics('tagset.csv')
        if 'tagset.csv' in os.getcwd():
            os.system('rm -r tagset.csv')
        stud_dict = stat_dict(df_stud)
        freq_dict = {}
        for entry in stud_dict:
            if entry in corpus_dict:
                freq_dict[entry] = corpus_dict[entry] + (stud_dict[entry])

        df_cor_stud = pd.Series(freq_dict).reset_index()
        df_cor_stud.columns = ['tagset', 'POS', 'freq']
        df_cor_stud[['corpus_freq', 'stud_txt_freq']] = pd.DataFrame(df_cor_stud['freq'].values.tolist(), index=df_cor_stud.index)
        del df_cor_stud['freq']
        t_stat, p_value = ttest_ind(df_cor_stud['corpus_freq'], df_cor_stud['stud_txt_freq'])
        if txt not in ttest_dict:
            ttest_dict[txt] = [t_stat, p_value]

    return ttest_dict

def ttest_summary(ttest_dict):
    if 'ttest_summary.csv' in os.getcwd():
        os.system('rm -r ttest_summary.csv')
    with open(('ttest_summary.csv'), 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['text_name', 't_statistics', 'p-value'])
        for entry in ttest_dict:
            writer.writerow([entry, ttest_dict[entry][0], ttest_dict[entry][1]])
    return print('Compiling t-test table for the given texts')

def main():
    ttest_summary(t_test(low_prsd))

if __name__ == "__main__":
        main()
