#!/usr/bin/python26
# -*- coding: iso-8859-2 -*-

import os, sys
import re
import time, random

import urlparse, unicodedata
import urllib2
from languages import LANGUAGES, HIRAGANA
#from urllib import urlopen, quote
from pytrie import SortedStringTrie as trie
from django.utils.encoding import smart_str, smart_unicode
from xml.dom.minidom import parseString

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
ENCODING =  'iso-8859-2'
MAXIMAL_DEPTH = 6
MAXIMAL_FOR = 2
LANG = 'pl'
TLD = 'pl'


# Code is a bit spaghetti, but who cares?

DEBUG = True

#PROXY_IP, PROXY_PORT = '222.165.130.82', 80

def get_suggestion(query, lang, tld):
    """Query Google suggest service"""
    suggestions = []

    if query:
        if isinstance(query, unicode): 
            query = query.encode('iso-8859-2')#encode('utf-8')
        
        query = query.replace(" ", "+")
        url = "http://clients1.google.%s/complete/search?hl=%s&q=%s&cp=1&output=toolbar" %(tld, lang, query)
        
        try:
            time.sleep( random.random() )
           
           # proxy_url = 'http://%s:%d' % (PROXY_IP, PROXY_PORT)

          #  proxy_support = urllib2.ProxyHandler({'http': proxy_url})
            opener = urllib2.build_opener()
            opener.addheaders = [('User-agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/534.30 (KHTML, like Gecko) Ubuntu/10.04 Chromium/12.0.742.112 Chrome/12.0.742.112 Safari/534.30')]
            
            urllib2.install_opener( opener )
            
            data = urllib2.urlopen( url ).read() 
          #  print "-------------- %s \n" % data
            data = smart_str(data.decode( ENCODING)) 
            
            return_array = []

            if not data:
               return []

            doc = parseString( data )
            
            nodes = doc.getElementsByTagName( 'CompleteSuggestion' )
 
            for node in nodes:
                phrase = node.firstChild.getAttribute( 'data' )
                count = node.lastChild.getAttribute( 'int' )
                return_array.append( (phrase, count) ) 
         
            return return_array
        except Exception as e:# as e:
            print " --------------- Critical error!!!!!!!"
            print e

    return suggestions

################################## 
trimRightWithLeading = lambda string : string.rstrip() + ' '    
replacePolishLetters = lambda string : unicodedata.normalize('NFKD', string.replace(u'ł', 'l')).encode('ascii', 'ignore')
numerOfWordInText = lambda string : len(string.split(' '))
leaveAccetableSigns = lambda string : re.sub( r'[^a-zA-Z0-9@&_\- ]', '', string )

def normalizePhrase(string):
   phrase = unicodedata.normalize('NFKD', string.replace(u'ł', 'l')).encode('ascii', 'ignore')
   re.sub(r'\W+_+', '', string)
   return string

counter = 5

##################################
def writeToFile(filename, content, type_f = 'a+'): 
   f = open(filename, type_f)
   f.write(content)
   f.close()


def grabWords(phrase, file_path, make_space_in_depth = True, level = 0, for_ = 0):
   global counter 
   
   phrase = phrase.rstrip()
   no_of_words = numerOfWordInText(phrase)

   grabbed_list = get_suggestion(phrase, LANG, TLD)
   grabbed_list_size = len(grabbed_list)

   if grabbed_list_size <= 1 or level > MAXIMAL_DEPTH or for_ > MAXIMAL_FOR:
      
      if grabbed_list_size == 1: # TODO: check when 1 and when 0
         if not trie_.has_key(grabbed_list[0][0]):
            counter += 1
            trie_.__setitem__( grabbed_list[0][0], None)#, grabbed_list[0][1] )
            print counter, smart_str (grabbed_list[0][0])#, smart_str(grabbed_list[0][1])
            content = "%s\n" % smart_str(grabbed_list[0][0])
            writeToFile( file_path, content )
         else:
            if DEBUG:
               print "MISS! :( -> " + smart_str (grabbed_list[0][0] ) 
            return
      else:
         return
   else: #elif grabbed_list_size > 1 :

      for (current_phrase, count) in grabbed_list:
         
         key, value = smart_str(current_phrase), count

         if not trie_.has_key( key ): 
            counter += 1
            trie_.__setitem__( key, None) #, value )
            content = "%s\n" % smart_str(key)
            writeToFile( file_path, content )
            print counter, key
         else:
            if DEBUG:
               print "MISS! (OUT) :( -> " + key + " === called( " + smart_str(phrase) + ")"
            return
        
   if grabbed_list_size == 10 and for_ < MAXIMAL_FOR:
      for_ += 1
      
      if True:
         for letter in ('a',u'ą','b','c',u'ć','d','e',u'ę','f','g','h','i','j','k','l',u'ł','m','n',u'ń','o',u'ó','p','q','r','s',u'ś','t','u','v','w','x','y','z',u'ż',u'ź','0','1','2','3','4','5','6','7','8','9',' '):   

            new_test_phrase = smart_str(phrase) + letter.encode('iso-8859-2')
         
            if make_space_in_depth:
               new_test_phrase = smart_str((phrase + ' ')) + letter.encode('iso-8859-2')

            grabbed_list_depper = get_suggestion(new_test_phrase, LANG, TLD)
            grabbed_list_depper_size = len(grabbed_list_depper)

            if grabbed_list_depper_size == 0: #TODO!!, realy? - how about 1
               continue
            elif grabbed_list_depper_size > 0: #TODO (do dziesieciu, a inczej print)
               l = level + 2
               if not trie_.has_key( new_test_phrase ):
                  grabWords(new_test_phrase, file_path, False, l, for_) # Reduce number of calls (print directly, not call scrobbler again)
           
def getAllSuggestion(phrase, file_path, intendations = True):
   cleared_phrase = leaveAccetableSigns(phrase)
   lowered_cleared = cleared_phrase.lower()
   grabWords(phrase, file_path, intendations)

def main():
   if len(sys.argv) != 3:
      print "Error usage, two parameters should been given"
   else: 
      getAllSuggestion(sys.argv[1], sys.argv[2])

if __name__ == "__main__":
    trie_ = trie()
    counter = 0
    main()



