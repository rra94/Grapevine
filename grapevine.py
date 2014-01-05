'''
This is designed for the new Azure Marketplace Bing Search API (released Aug 2012)

Inspired by https://github.com/mlagace/Python-SimpleBing and 
http://social.msdn.microsoft.com/Forums/pl-PL/windowsazuretroubleshooting/thread/450293bb-fa86-46ef-be7e-9c18dfb991ad
'''

import requests # Get from https://github.com/kennethreitz/requests
import string
import nltk
import os
import json
import alchemy
from urllib import urlopen
from urllib2 import HTTPError
from json import JSONEncoder

class BingSearchAPI():
    bing_api = "https://api.datamarket.azure.com/Data.ashx/Bing/Search/v1/Composite?"
    
    def __init__(self, key):
        self.key = key

    def replace_symbols(self, request):
        # Custom urlencoder.
        # They specifically want %27 as the quotation which is a single quote '
        # We're going to map both ' and " to %27 to make it more python-esque
        request = string.replace(request, "'", '%27')
        request = string.replace(request, '"', '%27')
        request = string.replace(request, '+', '%2b')
        request = string.replace(request, ' ', '%20')
        request = string.replace(request, ':', '%3a')
        return request
        
    def search(self, sources, query, params):
        ''' This function expects a dictionary of query parameters and values.
            Sources and Query are mandatory fields. 
            Sources is required to be the first parameter.
            Both Sources and Query requires single quotes surrounding it.
            All parameters are case sensitive. Go figure.

            For the Bing Search API schema, go to http://www.bing.com/developers/
            Click on Bing Search API. Then download the Bing API Schema Guide
            (which is oddly a word document file...pretty lame for a web api doc)
        '''
        request =  'Sources="' + sources    + '"'
        request += '&Query="'  + str(query) + '"'
        for key,value in params.iteritems():
            request += '&' + key + '=' + str(value) 
        request = self.bing_api + self.replace_symbols(request)
        return requests.get(request, auth=(self.key, self.key))

def find_all(s):
	sub = "u'Url': u'"
	st = 0
	start = []
	end = []
	while(True):
		if s.find(sub,st) == -1:
			zipped = zip(start,end)
			return zipped
		else:
			start.append(s.find(sub,st)+10)
			end.append(s.find("'",start[-1]))
			st = end[-1]



if __name__ == "__main__":
	my_key = "ZQAjwwE2px1ntdm3B56pZVTJ2fXW7Lqb46RKLApaqPg"
	query_file = open("queries.txt","r")
	lines = query_file.readlines()
	i = 0
	for i in xrange(len(lines)):
		query_string = lines[i][:-1]
		bing = BingSearchAPI(my_key)
		params = {'ImageFilters':'"Face:Face"','$format': 'json','$top': 10,'$skip': 0}
		target = open(query_string,'a')
		s= str(bing.search('web',query_string,params).json()) # requests 1.0+
		target.write(s)
		target.close()
		target = open(query_string,'r')
		s=target.read()
		target.close()
		zippy = find_all(s)
		#print len(zippy)
		urls=[]
		for j in xrange(len(zippy)):
			urls.append(s[zippy[j][0]:zippy[j][1]])
		target = open(query_string,'w')
		target.write(str(urls))
		target.close()
		os.system("python alchemyapi.py 979df1da4b76e6c5287258162076a3bf2840fb19")
		ctrpos = 0
		ctrneg = 0
		score = 0
		sentiment = ""
		for url in urls:
			try:
				html = urlopen(url).read()
			except IOError:
				continue
			raw = nltk.clean_html(html)  
			tup = alchemy.alchemical_response(raw)
			if tup[0] == "positive":
				ctrpos = ctrpos + 1
				score = score + float(tup[1])
			elif tup[0] == "negative":
				ctrneg = ctrneg + 1
				score = score + float(tup[1])
	
		if ctrpos > ctrneg:
			sentiment = "positive"
		elif ctrpos < ctrneg:
			sentiment = "negative"
		else:
			sentiment = "neutral"
    
		dict = {"agenda":query_string, "sentiment":sentiment, "score":score}
		#jsonString = JSONEncoder().encode(dict)
		filename = "Gujarat.txt"
		target = open(filename,"a")
		target.write(json.dumps(dict))
		target.write("\n")
		target.close()
	