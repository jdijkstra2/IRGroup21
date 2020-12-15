from bglinking.general_utils.str_to_dict import turn_into_dict

import ast

def get_first_paragraph(index_utils, docid):
   """
   returns the first paragraph of the document with docid in String form
   """
   raw_doc = index_utils.doc_raw(docid)

   raw_doc = raw_doc.replace(u'\xa0', u' ')
   doc_dict = turn_into_dict(raw_doc) 
   url = doc_dict['article_url']
   contents = doc_dict['contents']
   if len(contents) <= 0:
      print(url)
      print("Contents is empty!")
      print(raw_doc)
   else:
      for c in contents:
         if c == None:
            #print("c is none!")
            pass
         else:
            if 'subtype' in c.keys():
               if c['subtype'] == 'paragraph':
                  #print("Found first paragraph!")
                  first_paragraph = c['content']
                  break
      return first_paragraph 

