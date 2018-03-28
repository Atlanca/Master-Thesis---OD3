import xmlparser
import nlp
from gensim import corpora, models, similarities
from gensim.models import Phrases
import os
import re

import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
document_start = 11
document_end = 500
parser = xmlparser.XmlParser("snowflakethesis.xml")
document = parser.refactorAllText(7,10)
doc_paragraphs = []
mode = 0
min_sent_len_paragraph = 0


#We only want to work with paragraphs that have more than two sentences
for paragraph in document.paragraphs:
  if(paragraph.page >= document_start and paragraph.page <= document_end):
    if len(paragraph.paragraph.split('. ')) > min_sent_len_paragraph:
      doc_paragraphs.append(paragraph) 
      
#If we have saved files, just use them
#else create them
if (os.path.exists('snowflakethesisa.dict') and os.path.exists('snowflakethesisa.mm')):
  dictionary = corpora.Dictionary.load('snowflakethesis.dict')
  corpus = corpora.MmCorpus('snowflakethesis.mm')
  print('Used saved files')

else:
  text = ""
  tokenized_paragraphs = []

  #Tokenize paragraphs 
  for paragraph in doc_paragraphs:
    if(paragraph.page):
      related_titles = document.getRelatedTitles(paragraph.xmlTitle)
      text = ""
      
      #If mode is set to 1, we add titles to each paragraph
      if(mode == 1):
        for title in related_titles:
          text += title.title.lower() + "\n\n"
      
      text += paragraph.paragraph.lower() + "\n\n"
      tokenized_paragraphs.append(nlp.tokenize(text))
  
  #Compute bigrams
  bigram = Phrases(tokenized_paragraphs, min_count=2, threshold=10)
  bigram_tokenized_paragraphs = list(bigram[tokenized_paragraphs])
  
  #trigram = Phrases(bigram_tokenized_paragraphs, min_count=5, threshold=20)
  #bigram_tokenized_paragraphs = list(trigram[bigram_tokenized_paragraphs])
  
  #Create dictionary and save
  dictionary = corpora.Dictionary(bigram_tokenized_paragraphs)
  dictionary.save('snowflakethesis.dict')
  corpus = [dictionary.doc2bow(paragraph) for paragraph in bigram_tokenized_paragraphs]
  corpora.MmCorpus.serialize('snowflakethesis.mm', corpus)
  
  print("Created files")

#1. Initialize corpus
tfidf = models.TfidfModel(corpus)
corpus_tfidf = tfidf[corpus]

#2. Use LSI
chunk_size = 200
power_iters = 5

lsi = models.LsiModel(corpus_tfidf, id2word=dictionary, chunksize = chunk_size, power_iters=power_iters)
corpus_lsi = lsi[corpus_tfidf]

#Create index
if os.path.exists('snowflakethesisa.index'):
  index = similarities.MatrixSimilarity.load('snowflakethesis.index')
else:
  index = similarities.MatrixSimilarity(lsi[corpus])
  index.save('snowflakethesis.index')

#Input query
query = ''
while query != 'exit':
  
  query = input('Enter query: ')
  
  #Check bigrams are ok
  #Else check relevancy of query to document
  if query == 'bigrams':
    unique_words = []
    for wordlist in bigram_tokenized_paragraphs:
      for word in wordlist:
        if '_' in word and word not in unique_words:
          unique_words.append(word)
       
  else:
    #Checks how relevant the query is to the document
    split_query = query.split('_')
    tokenized_query = []
    for phrase in split_query:
      tokenized = nlp.tokenize(phrase) 
      if tokenized_query:
        tokenized_query[-1] = tokenized_query[-1] + '_' + tokenized[0]
        tokenized = tokenized[1:]
        tokenized_query += tokenized
      else:
        tokenized_query += tokenized
       
    vec_bow = dictionary.doc2bow(tokenized_query)
    vec_lsi = lsi[vec_bow]

    #Performing query on each document
    sims = index[vec_lsi]
    sims = sorted(enumerate(sims), key=lambda item: -item[1])

    #Collects the first 10 results
    found_paragraphs = []
    for i in range(0,10):
      pos, score = sims[i]
      found_paragraphs.append((score, doc_paragraphs[pos]))
    
    #Sort the 10 paragraphs by their id (used to know which order the paragraphs are found in the text)
    #And print, also print the words from the query that were found in the dictionary
    for (s,p) in sorted(found_paragraphs, key=lambda p:p[-1].id):   
      print(str(s) + ': ' + p.xmlTitle.title + ', id: ' + str(p.id)+ ', page: ' + str(p.page) + '\n' + p.paragraph + '\n\n')
    for word_id, exist in vec_bow:
      print(dictionary[word_id])

    #print(query)
    print(tokenized_query)

