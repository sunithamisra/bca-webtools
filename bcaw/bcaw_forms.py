#!/usr/bin/python
# coding=UTF-8
#
# BitCurator Access Webtools (Disk Image Access for the Web)
# Copyright (C) 2014
# All rights reserved.
#
# This code is distributed under the terms of the GNU General Public
# License, Version 3. See the text file "COPYING" for further details
# about the terms of this license.
#
# This file contains the flask forms for BitCurator Access webtools.
# Ref: http://code.tutsplus.com/tutorials/intro-to-flask-signing-in-and-out--net-29982
#

from flask.ext.wtf import Form 
from wtforms import TextField, TextAreaField, SubmitField, validators, ValidationError, PasswordField
from bcaw_userlogin_db import User, db_login
import bcaw_db
 
class ContactForm(Form):
  name = TextField("Name")
  email = TextField("Email")
  subject = TextField("Subject")
  message = TextAreaField("Message")
  submit = SubmitField("Send")

class SignupForm(Form):
    firstname = TextField("First name",  [validators.Required("Please enter your first name.")])
    lastname = TextField("Last name",  [validators.Required("Please enter your last name.")])
    email = TextField("Email",  [validators.Required("Please enter your email address."), validators.Email("Please enter your email address.")])
    password = PasswordField('Password', [validators.Required("Please enter a password.")])
    submit = SubmitField("Create account")
 
    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
 
    def validate(self):
        if not Form.validate(self):
            return False
     
        user = User.query.filter_by(email = self.email.data.lower()).first()
        if user:
            self.email.errors.append("That email is already taken")
            return False
        else:
            return True
        return True

class SigninForm(Form):
  email = TextField("Email",  [validators.Required("Please enter your email address."), validators.Email("Please enter your email address.")])
  password = PasswordField('Password', [validators.Required("Please enter a password.")])
  submit = SubmitField("Sign In")
   
  def __init__(self, *args, **kwargs):
    Form.__init__(self, *args, **kwargs)
 
  def validate(self):
    if not Form.validate(self):
      return False
     
    user = User.query.filter_by(email = self.email.data.lower()).first()
    if user and user.check_password(self.password.data):
      return True
    else:
      self.email.errors.append("Invalid e-mail or password")
      return False

class QueryForm(Form):
    #search_text = TextField("Search", [validators.Required("Please enter the search phrase"), validators.DataRequired("Please enter the search phrase") )
    search_text = TextField("Search" )
    submit = SubmitField("Search")
    search_result = []
    q1 = []
    q2 = []

    print "D: Search_text: ", search_text
    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

    def searchDfxmlDb(self):
        print "D: Search_text: ", self.search_text.data.lower()
        if not Form.validate(self):
            print("D: bcaw_forms: Validate failed. returning ");
            return None

        search_text_query = '%' + self.search_text.data.lower() + '%'
        print "search_text_query = ", search_text_query

        q1 = bcaw_db.BcawDfxmlInfo.query.filter(bcaw_db.BcawDfxmlInfo.fo_filename.ilike(search_text_query))
        print("Query: ", q1.limit(5).all())

        q2 = q1.all()
        if len(q2) == 0:
            print "Query: Not found: ", self.search_text.data.lower()
            return None
        last_elem = len(q2) - 1
        print "D: Length-1: ", last_elem
        return q2
        
