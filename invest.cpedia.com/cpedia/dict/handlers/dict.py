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
import BeautifulSoup import BeautifulSoup

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
        try:
            terms_page = urlfetch.fetch(
                    url="http://www.investopedia.com/terms/1/?viewed=1",
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
                    term.content = utils.utf82uni(term_a.prettify().replace("[\n]",""))
                    terms+=[term]
            current_date = datetime.datetime.now().strftime('%b %d %Y')
            latest_deals = []
            for deal in terms:
                deal_ = models.Deals.gql('where created_date_str =:1 and title =:2',current_date,deal.title).fetch(10)
                if deal_ and len(deal_) > 0:
                    break
                else:
                    latest_deals += [deal]
            for latest_deal in reversed(latest_deals):
                latest_deal.created_date = datetime.datetime.now()   #unaccuracy for the auto_now_add
                latest_deal.put()
            template_values = {
            "msg":"Generate latest deals from dealsea.com successfully.",
            }
        except Exception, exception:
            mail.send_mail(sender="deal.checklist.cc <cpedia@checklist.cc>",
                           to="Ping Chen <cpedia@gmail.com>",
                           subject="Something wrong with the Deal Generation Job.",
                           body="""
Hi Ping,

Something wroing with the Deal Generation Job.

Below is the detailed exception information:
%s

Please access app engine console to resolve the problem.
http://appengine.google.com/a/checklist.cc

Sent from deal.checklist.cc
            """ % traceback.format_exc())

            template_values = {
            "msg":"Generate latest deals from dealsea.com unsuccessfully. An alert email sent out.<br>" + traceback.format_exc(),
            }

        self.generate('dict.html',template_values)

    def post(self):
        self.get()
