import nltk.data
import nlp
from gensim import corpora, models, similarities
from gensim.models import Phrases
from gensim.models import TfidfModel
from gensim.corpora import Dictionary
import xmlparser
import re

# document_start = 11
# document_end = 500
# parser = xmlparser.XmlParser("snowflakethesis.xml")
# document = parser.refactorAllText(7,10)
# mode = 0
# min_sent_len_paragraph = 0

# tokenized_paragraphs = []

# #Tokenize paragraphs 
# for paragraph in document.paragraphs:
#     if(paragraph.page):
#         tokenized_paragraphs.append(nlp.tokenize(paragraph.paragraph))
  
#     #Compute bigrams
#     bigram = Phrases(tokenized_paragraphs, min_count=2, threshold=10)
    
# # dictionary = corpora.Dictionary(bigram_tokenized_paragraphs)
# # corpus = [dictionary.doc2bow(paragraph) for paragraph in bigram_tokenized_paragraphs]


tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')

# Open txt file
f = open('LogicalClassDiagramText.txt', 'r')
text = f.read()
f.close()

sentences = tokenizer.tokenize(text)
sentenceTokens = [nlp.lemmaTokenize(sentence) for sentence in sentences]
dct = Dictionary(sentenceTokens)

corpus = [dct.doc2bow(sentence) for sentence in sentenceTokens]

dictionary = [[(dct[wordId[0]], wordId[1]) for wordId in sentence] for sentence in corpus]

tfidf = models.TfidfModel(corpus)
corpus_tfidf = tfidf[corpus]

corpus_tfidf_words = [[(dct[wordId[0]], wordId[1]) for wordId in sentence] for sentence in corpus_tfidf]

lsi = models.LsiModel(corpus, id2word=dct, num_topics=10)

doc = 'order'
vec_bow = dct.doc2bow(doc.lower().split())
vec_lsi = lsi[vec_bow]

index = similarities.MatrixSimilarity(lsi[corpus])
sims = index[vec_lsi] # perform a similarity query against the corpus
sims = sorted(enumerate(sims), key=lambda item: -item[1])

relatedSentences = []

for index, sentence in enumerate(sims):
    if(sentence[1] > 0.3 and index < 6):
        relatedSentences.append((sentences[sentence[0]], sentence[1]))
        text = re.sub(r'(' + re.escape(sentences[sentence[0]]) + ')', r'<font color="red">\1</font>', text)

print(text)

f = open('editedLogicalDiagramText.txt', 'w')
f.write(text)
f.close()

# sentences = tokenizer.tokenize(text)
# lemmatizedSentences = [nlp.lemmaTokenize(sentence) for sentence in sentences]

# bigram_tokenized_paragraphs = list(bigram[lemmatizedSentences])

# print('Something')
# print(bigram_tokenized_paragraphs)
# fullText = [word for sentence in bigram_tokenized_paragraphs for word in sentence]
# print(nlp.chunkText(fullText))

