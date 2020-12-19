from bglinking.general_utils.str_to_dict import turn_into_dict
from bs4 import BeautifulSoup
from tqdm import tqdm
import nltk
nltk.download('punkt')
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
nltk.download('stopwords')

import ast

def get_first_paragraph(index_utils, docid):
   """
   Returns the words in the first paragraph of a document, along with the words of the title
   """
   
   # the following terms will not count as words
   garbage_terms = [',', '.', '&', '-', '"', '`', ' ', '_', '$', '%', '#', '@', '*', '(', ')', '``', '\'\'', '\"', '\"\"', '--', '..', '...', '....']

   ps = PorterStemmer()
   
   # obtain contents of the document
   raw_doc = index_utils.doc_raw(docid).replace(u'\xa0', u' ')

   # convert to dictionary
   doc_dict = turn_into_dict(raw_doc) 

   url = doc_dict['article_url']
   contents = doc_dict['contents']
      
   words_list = []

   for c in contents:
      if c == None:
         pass
      else:
         if 'subtype' in c.keys():

            # only consider paragraphs
            if c['subtype'] == 'paragraph':

               # extract the content
               first_paragraph = c['content']
               
               # remove html markup
               first_paragraph = BeautifulSoup(first_paragraph, "lxml").text
               
               # tokenize the paragraph
               words = word_tokenize(first_paragraph)

               # remove garbage words and stopwords
               words = [word for word in words if word not in garbage_terms and len(word) > 2 and word not in stopwords.words('english')]
               
               if len(words) > 20:
                  # if this was the 'real' first paragraph, and not a short 'clickbait' oneliner
                  words_list += words
                  break
   
   # add the title words
   title = doc_dict['title']

   if title:
      title_words = word_tokenize(title)
      title_words = [word for word in title_words if word not in garbage_terms and len(word) > 2 and word not in stopwords.words('english')]
      words_list += title_words   

   # stem all words            
   for i in range(len(words_list)):
      words_list[i] = ps.stem(words_list[i])

   return words_list


   
   
    
      
      
