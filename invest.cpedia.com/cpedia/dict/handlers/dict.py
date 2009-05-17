# !/usr/bin/env python
#
# Copyright 2008 CPedia.com.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

__author__ = 'Ping Chen'

import cgi
import wsgiref.handlers
import os
import re
import datetime
import calendar
import logging
import string
import urllib
import traceback 

from xml.etree import ElementTree

from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.api import memcache
from google.appengine.ext import search
from google.appengine.api import images
from google.appengine.api import mail

from cpedia.dict.handlers import restful
import cpedia.dict.models.dict as models
from cpedia.utils import utils

import simplejson
import authorized
import view
import config

import sys
import urllib
from google.appengine.api import urlfetch

from BeautifulSoup import BeautifulSoup

class BaseRequestHandler(webapp.RequestHandler):
    """Supplies a common template generation function.

    When you call generate(), we augment the template variables supplied with
    the current user in the 'user' variable and the current webapp request
    in the 'request' variable.
    """
    def generate(self, template_name, template_values={}):
        values = {
        #'archiveList': util.getArchiveList(),
        }
        values.update(template_values)
        view.ViewPage(cache_time=0).render(self, template_name, values)

    def generate_dictionary(self,alphabetical):
        try:
            terms_page = urlfetch.fetch(
                    url="http://www.investopedia.com/terms/%s/?viewed=1" % alphabetical,
                    method=urlfetch.GET,
                    headers={'Content-Type': 'text/html; charset=UTF-8'}
                    )
            terms = []
            if terms_page.status_code == 200:
                term_soap = BeautifulSoup(terms_page.content)
                term_span = term_soap.find("span",id="Span1")
                links = term_span.findAll("a")
                for link in links:
                    term = models.Terms(alphabetical="#")
                    term.term = utils.utf82uni(str(link.contents[0]))
                    url_quote = link.get("href").replace(".asp","").replace("/terms/","").split("/")
                    term.alphabetical = url_quote[0]
                    term.term_url_quote = url_quote[1]
                    term_ = models.Terms.gql('where term_url_quote =:1',term.term_url_quote).fetch(10)
                    if term_ and len(term_) > 0:
                        pass
                    else:
                        terms+=[term]
            for term in reversed(terms):
                term.put()
            template_values = {
            "msg":"Generate dictionary terms from investopedia.com successfully.",
            }
        except Exception, exception:
            mail.send_mail(sender="invest.cpedia.com <cpedia@gmail.com>",
                           to="Ping Chen <cpedia@gmail.com>",
                           subject="Something wrong with the dictionary terms Generation Job.",
                           body="""
Hi Ping,

Something wroing with the dictionary terms Generation Job.

Below is the detailed exception information:
%s

Please access app engine console to resolve the problem.
http://appengine.google.com/a/cpedia.com

Sent from invest.cpedia.com
            """ % traceback.format_exc())

            template_values = {
            "msg":"Generate dictionary terms from investopedia.com unsuccessfully. An alert email sent out.<br>" + traceback.format_exc(),
            }

        self.generate('dict.html',template_values)


class NotFoundHandler(webapp.RequestHandler):
    def get(self):
        self.error(404)
        view.ViewPage(cache_time=36000).render(self,"notfound.html")

class UnauthorizedHandler(webapp.RequestHandler):
    def get(self):
        self.error(403)
        view.ViewPage(cache_time=36000).render(self,"unauthorized.html")

class MainPage(BaseRequestHandler):
    def get(self):
        user = users.get_current_user()
        template_values = {
        }
        self.generate('dict.html',template_values)

class GetTermsJob(BaseRequestHandler):
    def get(self):
    #if self.get("X-AppEngine-Cron")=="true":
         self.generate_dictionary("1")

    def post(self):
        self.get()

class GetTermsJobAtoZ(BaseRequestHandler):
    def get(self,alphabetical):
    #if self.get("X-AppEngine-Cron")=="true":
         self.generate_dictionary(alphabetical)

