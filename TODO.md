# CATandkittens_2019-2021
Репозиторий для проекта Catandkittens НИУ ВШЭ, курс - компьютерная лингвистика

## где искать информацию о udpipe'е
* https://pypi.org/project/ufal.udpipe/
* http://ufal.mff.cuni.cz/udpipe/users-manual

## Замечания о работе над морфологией
* Можно построить две таблицы с тэгсэтами:
  1. Одна для всех слов кроме существительных и для неё высчитать частотность: словоформа - тэгсэт
  2. Другая для существительных, тк существительные подробнее описаны и стоит имеет стольбцы с описанием рода, числа и тд.
  
* Можно и побольше таблиц построить, чтобы разные POS описать

## Примеры из студ текстов

#### text = я не знаю нуансы этой аргументы.
1	я	я	PROPN	NNMS1-----A----	Animacy=Anim|Case=Nom|Gender=Masc|NameType=Sur|Number=Sing|Polarity=Pos	0	root	_	_
2	не	не	PROPN	NNMS1-----A----	Animacy=Anim|Case=Nom|Gender=Masc|NameType=Sur|Number=Sing|Polarity=Pos	1	flat	_	_
3	знаю	знаю	PROPN	NNMS1-----A----	Animacy=Anim|Case=Nom|Gender=Masc|NameType=Sur|Number=Sing|Polarity=Pos	1	flat	_	_
4	нуансы	нуансы	PROPN	NNMS1-----A----	Animacy=Anim|Case=Nom|Gender=Masc|NameType=Sur|Number=Sing|Polarity=Pos	1	flat	_	_
5	этой	этой	PROPN	NNMS1-----A----	Animacy=Anim|Case=Nom|Gender=Masc|NameType=Sur|Number=Sing|Polarity=Pos	1	dep	_	_
6	аргументы	аргументы	PROPN	NNMS1-----A----	Animacy=Anim|Case=Nom|Gender=Masc|NameType=Sur|Number=Sing|Polarity=Pos	5	flat	_	SpaceAfter=No
7	.	.	PUNCT	Z:-------------	_	1	punct	_	SpaceAfter=No

#### text = Я родилься в Америке, но мой родительи родились в Украйне.
1	Я	я	PRON	_	Case=Nom|Number=Sing|Person=1	2	nsubj	_	_
2	родилься	родилься	VERB	_	Aspect=Perf|VerbForm=Inf|Voice=Mid	0	root	_	_
3	в	в	ADP	_	_	4	case	_	_
4	Америке	Америка	PROPN	_	Animacy=Inan|Case=Loc|Gender=Fem|Number=Sing	2	obl	_	SpaceAfter=No
5	,	,	PUNCT	_	_	9	punct	_	_
6	но	но	CCONJ	_	_	9	cc	_	_
7	мой	мой	DET	_	Case=Nom|Gender=Masc|Number=Sing	8	det	_	_
8	родительи	родителей	NOUN	_	Animacy=Inan|Case=Nom|Gender=Masc|Number=Plur	9	nsubj	_	_
9	родились	рождаться	VERB	_	Aspect=Perf|Mood=Ind|Number=Plur|Tense=Past|VerbForm=Fin|Voice=Mid	2	conj	_	_
10	в	в	ADP	_	_	11	case	_	_
11	Украйне	Украйн	PROPN	_	Animacy=Inan|Case=Loc|Gender=Masc|Number=Sing	9	obl	_	SpaceAfter=No
12	.	.	PUNCT	_	_	2	punct	_	_

#### text = Она будем приводить меня обратна к миру и не даст мне терятса в моей голове.
1	Она	она	PRON	_	Case=Nom|Gender=Fem|Number=Sing|Person=3	3	nsubj	_	_
2	будем	быть	AUX	_	Aspect=Imp|Mood=Ind|Number=Plur|Person=1|Tense=Pres|VerbForm=Fin|Voice=Act	3	aux	_	_
3	приводить	приводить	VERB	_	Aspect=Imp|VerbForm=Inf|Voice=Act	0	root	_	_
4	меня	я	PRON	_	Case=Acc|Number=Sing|Person=1	3	obj	_	_
5	обратна	обратный	ADJ	_	Degree=Pos|Gender=Fem|Number=Sing|Variant=Short	3	obl	_	_
6	к	к	ADP	_	_	7	case	_	_
7	миру	мир	NOUN	_	Animacy=Inan|Case=Dat|Gender=Masc|Number=Sing	5	obl	_	_
8	и	и	CCONJ	_	_	10	cc	_	_
9	не	не	PART	_	_	10	advmod	_	_
10	даст	дать	VERB	_	Aspect=Perf|Mood=Ind|Number=Sing|Person=3|Tense=Fut|VerbForm=Fin|Voice=Act	5	conj	_	_
11	мне	я	PRON	_	Case=Dat|Number=Sing|Person=1	10	iobj	_	_
12	терятса	терятс	NOUN	_	Animacy=Inan|Case=Gen|Gender=Masc|Number=Sing	10	obl	_	_
13	в	в	ADP	_	_	15	case	_	_
14	моей	мой	DET	_	Case=Loc|Gender=Fem|Number=Sing	15	det	_	_
15	голове	голова	NOUN	_	Animacy=Inan|Case=Loc|Gender=Fem|Number=Sing	10	obl	_	SpaceAfter=No
16	.	.	PUNCT	_	_	3	punct	_	_

#### Пример
37	друзя	друзь	VERB	_	Aspect=Imp|Tense=Pres|VerbForm=Conv|Voice=Act	25	parataxis	_	SpaceAfter=No

## Замечания о примерах
* В большинстве случаев неправильно написанные слова просто не существуют. Их, мб, можно испавить с помощью спелчекера.
* Когда род неправилен, тэгсэт будет неправильным. Тогда вот то слово можно выделить.
