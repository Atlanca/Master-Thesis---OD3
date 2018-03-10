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


#We only want to work with paragraphs that have more than two sentences
for paragraph in document.paragraphs:
  if(paragraph.page >= document_start and paragraph.page <= document_end):
    if len(paragraph.paragraph.split('. ')) > 0:
      doc_paragraphs.append(paragraph) 
      
#If we have saved files, just use them
#else create them
if (os.path.exists('snowflakethesis.dict') and os.path.exists('snowflakethesis.mm')):
  dictionary = corpora.Dictionary.load('snowflakethesis.dict')
  corpus = corpora.MmCorpus('snowflakethesis.mm')
  print('Used saved files')

else:
  text = ""
  prevTitle = ""
  tokenizedParagraphs = []

  #Tokenize paragraphs 
  for paragraph in doc_paragraphs:
    if(paragraph.page):
      relatedTitles = document.getRelatedTitles(paragraph.xmlTitle)
      text = ""
      
      #If mode is set to 1, we add titles to each paragraph
      if(mode == 1):
        for title in relatedTitles:
          text += title.title.lower() + "\n\n"
      
      text += paragraph.paragraph.lower() + "\n\n"
      tokenizedParagraphs.append(nlp.tokenize(text))
  
  #Compute bigrams
  bigram = Phrases(tokenizedParagraphs, min_count=2, threshold=10)
  bigramTokenizedParagraphs = list(bigram[tokenizedParagraphs])
  
  #trigram = Phrases(bigramTokenizedParagraphs, min_count=5, threshold=20)
  #bigramTokenizedParagraphs = list(trigram[bigramTokenizedParagraphs])
  
  #Create dictionary and save
  dictionary = corpora.Dictionary(bigramTokenizedParagraphs)
  dictionary.save('snowflakethesis.dict')
  corpus = [dictionary.doc2bow(paragraph) for paragraph in bigramTokenizedParagraphs]
  corpora.MmCorpus.serialize('snowflakethesis.mm', corpus)
  
  print("Created files")

#1. Initialize corpus
tfidf = models.TfidfModel(corpus)
corpus_tfidf = tfidf[corpus]

#2. Use LSI
chunkSize = 200
powerIters = 5

lsi = models.LsiModel(corpus_tfidf, id2word=dictionary, chunksize = chunkSize, power_iters=powerIters)
corpus_lsi = lsi[corpus_tfidf]

#Create index
if os.path.exists('snowflakethesis.index'):
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
    for wordlist in bigramTokenizedParagraphs:
      for word in wordlist:
        if '_' in word and word not in unique_words:
          unique_words.append(word)
       
  else:
    #Checks how relevant the query is to the document
    splitQuery = query.split('_')
    tokenizedQuery = []
    for phrase in splitQuery:
      tokenized = nlp.tokenize(phrase) 
      print(tokenized)
      if tokenizedQuery:
        tokenizedQuery[-1] = tokenizedQuery[-1] + '_' + tokenized[0]
        tokenized = tokenized[1:]
        tokenizedQuery += tokenized
      else:
        tokenizedQuery += tokenized
       
    vec_bow = dictionary.doc2bow(tokenizedQuery)
    vec_lsi = lsi[vec_bow]

    #Performing query on each document
    sims = index[vec_lsi]
    sims = sorted(enumerate(sims), key=lambda item: -item[1])

    #Collects the first 10 results
    foundParagraphs = []
    for i in range(0,10):
      pos, score = sims[i]
      foundParagraphs.append((score, doc_paragraphs[pos]))
    
    #Sort the 10 paragraphs by their id (used to know which order the paragraphs are found in the text)
    #And print, also print the words from the query that were found in the dictionary
    for (s,p) in sorted(foundParagraphs, key=lambda p:p[-1].id):   
      print(str(s) + ': ' + p.xmlTitle.title + ', id: ' + str(p.id)+ ', page: ' + str(p.page) + '\n' + p.paragraph + '\n\n')
    for wordId, exist in vec_bow:
      print(dictionary[wordId])

    print(query)
    print(tokenizedQuery)

