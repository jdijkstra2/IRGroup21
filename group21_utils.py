from bglinking.general_utils.str_to_dict import turn_into_dict
from bs4 import BeautifulSoup
from tqdm import tqdm
import nltk
nltk.download('punkt')
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize

import ast

def get_first_paragraph(index_utils, docid):
   """
   returns the first paragraph of the document with docid in the form of a List of Strings
   """
   garbage_terms = [',', '.', '&', '-', '"', '`', ' ', '_', '$', '%', '#', '@', '*', '(', ')', '``', '\'\'', '\"', '\"\"', '--', '..', '...', '....']

   only_first_paragraph = False
   only_first_real_paragraph = False
   both = True

   ps = PorterStemmer()

   raw_doc = index_utils.doc_raw(docid).replace(u'\xa0', u' ')
   doc_dict = turn_into_dict(raw_doc) 
   url = doc_dict['article_url']

   contents = doc_dict['contents']
   words_list = []

   for c in contents:
      if c == None:
         pass
      else:
         if 'subtype' in c.keys():
            if c['subtype'] == 'paragraph':
               first_paragraph = c['content']
               first_paragraph = BeautifulSoup(first_paragraph, "lxml").text
               
               words = word_tokenize(first_paragraph)
               words = [word for word in words if word not in garbage_terms and len(word) > 1]
               words_list += words

               if both:
                  if len(words_list) > 20:
                     break
               elif only_first_paragraph:
                  if len(words_list) > 0:
                     break
               elif only_first_real_paragraph:
                  pass

   for i in range(len(words_list)):
      words_list[i] = ps.stem(words_list[i])

   #print(len(words_list))
   return words_list


   
   
    
      
      
