from bglinking.general_utils.str_to_dict import turn_into_dict
from bs4 import BeautifulSoup
import nltk
nltk.download('punkt')
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize

import ast

def get_first_paragraph(index_utils, docid):
   """
   returns the first paragraph of the document with docid in the form of a List of Strings
   """
   ps = PorterStemmer()

   raw_doc = index_utils.doc_raw(docid)

   raw_doc = raw_doc.replace(u'\xa0', u' ')
   doc_dict = turn_into_dict(raw_doc) 
   url = doc_dict['article_url']
   contents = doc_dict['contents']
   for c in contents:
      if c == None:
         #print("c is none!")
         pass
      else:
         if 'subtype' in c.keys():
            if c['subtype'] == 'paragraph':
               first_paragraph = c['content']
               first_paragraph = BeautifulSoup(first_paragraph, "lxml").text
               if len(first_paragraph) != 0:
                  break
   words_list = word_tokenize(first_paragraph)
   for i in range(len(words_list)):
      words_list[i] = ps.stem(words_list[i])
   return words_list

