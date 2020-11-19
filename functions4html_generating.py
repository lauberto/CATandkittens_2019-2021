# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 00:59:07 2020

@author: user
"""
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
    return conllu_sents
            

##Функция вносит в данные юдипайпа информацию из яндекс-чекера о том, есть ли в слове орфогрфическая ошибка
def add_spelling_problems_info(conllu_sents, text_spelling_problems):
    current_spelling_problem_id = 0
    current_spelling_problem = text_spelling_problems[current_spelling_problem_id]
    current_spelling_problem_end = current_spelling_problem['pos'] + current_spelling_problem['len']
    current_spelling_problem['end_id'] = current_spelling_problem_end
    for sent in conllu_sents:
        for token in sent.tokens:
        #Если зашли дальше конца текущей ошибки, переходим к следующей или заканчиваем
            if token['end_id'] > current_spelling_problem_end:
                if current_spelling_problem_id < len(text_spelling_problems) - 1:
                    current_spelling_problem_id += 1
                    current_spelling_problem = text_spelling_problems[current_spelling_problem_id]
                    current_spelling_problem_end = current_spelling_problem['pos'] + current_spelling_problem['len']
                    current_spelling_problem['end_id'] = current_spelling_problem_end
                else:
                    break
                    break
            if token['start_id'] >= current_spelling_problem['pos']:
                token['is_spelling_error'] = True
    return conllu_sents

##Выставляются только содержательные выделения, добавить графические
def get_class(substring_with_metadata):
    class_ = None
    if substring_with_metadata['problem_type']:
        if substring_with_metadata['problem_type'] == 'spelling':
            class_ = 'spelling'
    return class_

def add_tags(text, substringsWithMetadata, tag_type='strong'):
    substringsWithMetadata = sorted(substringsWithMetadata, key = lambda x: x['pos'], reverse = True)
    for substring in substringsWithMetadata:
        class_ = get_class(substring)
        if class_:
            prefix = '<'+tag_type+' class="'+ class_+'">'
            postfix = '</'+ tag_type + '>'
            text = text[:substring['pos']] + prefix + substring['word'] + postfix + text[substring['end']:]
    return text

##Функция принимает объект python.Docx и возвращает данные о расположении графических выделений соответствующем ему полном тексте
def get_font_info(docx_obj, run_attrs = ['bold', 'italic'], font_attrs = ['subscript']):
    highlighting_types = {}
    for attr in run_attrs:
        highlighting_types[attr] = []
    for attr in font_attrs: 
        highlighting_types[attr] = []
    num_prev_symb = 0
    for paragraph in docx_obj.paragraphs:
        for run in paragraph.runs:
            run_end = num_prev_symb + len(run.text)
            for attr in run_attrs:
                if hasattr(run, attr) and getattr(run, attr):
                    highlighting_types[attr].append({'pos': num_prev_symb, 'end': run_end, 'highlighting_type': attr})
            for attr in font_attrs:
                if hasattr(run.font, attr) and getattr(run.font, attr):
                    highlighting_types[attr].append({'pos': num_prev_symb, 'end': run_end, 'highlighting_type': attr})
                num_prev_symb = run_end
        ##Так как в тексте будет символ разрыва абзац,
        num_prev_symb += 1
        
    def join_neighboring(highlightings):
        if len(highlightings) > 2:
            joined_highlighting = []
            current_highlighting = highlightings[0]
            for next_highlighting in highlightings[1:]:
                if current_highlighting['end']+1 == next_highlighting['pos']:
                    current_highlighting['end'] = next_highlighting['end']
                else:
                    joined_highlighting.append(current_highlighting)
                    current_highlighting = next_highlighting
            if joined_highlighting[-1]['end'] != current_highlighting['end']:
                joined_highlighting.append(current_highlighting)
            highlightings = joined_highlighting
        return highlightings
    
    highlightings = []
    for i in highlighting_types:
        highlightings += join_neighboring(highlighting_types[i])
    
    return highlightings

