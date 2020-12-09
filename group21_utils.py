from bglinking.general_utils.str_to_dict import turn_into_dict

import ast

def get_first_paragraph(index_utils, docid):
   """
   returns the first paragraph of the document with docid in String form
   """
   raw_doc = index_utils.doc_raw(docid)

   if type(raw_doc) != str:
      print("raw_doc should be of type str!")
      return ""
   else:
      raw_doc = raw_doc.replace(u'\xa0', u' ')
      doc_dict = turn_into_dict(raw_doc) 
      #doc_dict = ast.literal_eval(raw_doc)
      url = doc_dict['article_url']
      print(url)
      contents = doc_dict['contents']
      for c in contents:
         if 'subtype' in c.keys():
            if c['subtype'] == 'paragraph':
               first_paragraph = c['content']
               break
      return first_paragraph 

