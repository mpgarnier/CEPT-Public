import json
import random
import urllib
import urllib2

import numpy as np


class CeptClient(object):

    def __init__(self, apiKey=None, apiServer="http://api.cortical.io", retinaName="eng_syn"):
        #if apiKey == None:
        #    raise Exception('You must pass an apiKey when instantiating the APIClient.')
        self.apiKey = apiKey
        self.apiServer = apiServer
        self.retinaName = retinaName


    def getSimilarTerms(self, positions, howMany):
        """given a list of positions (SDR, indices of on-bits), returns a list of the most similar terms 
        (in decreasing order)"""
        if not positions:
            return "--"
        #print "getSimTerms", type(positions), positions
        expr = '{ "positions":  %s }' % (str(positions))
        res = []
        try:
            simTerms = self.callAPI("/rest/expressions/similarTerms?api_key=%s&retinaName=%s&start-index=0&max-results=%i" % (self.apiKey, self.retinaName, howMany), "POST", expr)
            res = [term['term'] for term in simTerms[:howMany]]
        except Exception, e:
            print "getSimilarTerms", e
        return res


    def getSDR(self, term):
        """given a term, convert this into a semantic SDR, returned as a list of positions"""
        expr = '{ "term": "%s"}' % (term)
        return self.getSDRexpr(expr)

    def getSDRexpr(self, expression):
        """given an expression, convert this into a semantic SDR, returned as a list of positions"""
        res = []
        #print expression
        try:
            res = self.callAPI("/rest/expressions?api_key=%s&retinaName=%s" % (self.apiKey, self.retinaName), "POST", expression)[0]['positions']
        except Exception, e:
            print "getSDR", e
        return res


    def getSimilarTermsForTerm(self, term):
        res = []
        try:
            res = self.callAPI("/rest/terms/similarTerms?api_key=%s&retinaName=%s&start-index=0&max-results=20&term=%s" % (self.apiKey, self.retinaName, urllib.quote(term)), "GET", None)
        except Exception, e:
            print e
        return res

    def getContextsForTerm(self, term):
        res = []
        try:
            res = self.callAPI("/rest/terms/contexts?api_key=%s&retinaName=%s&start-index=0&max-results=10&term=%s" % (self.apiKey, self.retinaName, urllib.quote(term)), "GET", None)
        except Exception, e:
            print e
        return res


    ############

    def callAPI(self, resourcePath, method, postData):
        url = self.apiServer + resourcePath
        data = postData
        headers = {}

        if method in ['GET']:
            pass
        elif method in ['POST', 'PUT', 'DELETE']:
            if postData:
                headers['Content-type'] = 'application/json'
        else:
            raise Exception('Method ' + method + ' is not recognized.')

        request = urllib2.Request(url=url.encode('utf-8'), headers=headers, data=data)
        response = urllib2.urlopen(request)
        string = response.read()

        try:
            data = json.loads(string)
        except ValueError:  # PUT requests don't return anything
            data = None

        return data
