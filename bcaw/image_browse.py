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
# This file contains the main BitCurator Access Webtools application.
#

from flask import Flask, render_template, url_for, Response, stream_with_context, request, flash, session, redirect
from bcaw_forms import ContactForm, SignupForm, SigninForm, QueryForm

import pytsk3
import os, sys, string, time, re
from mimetypes import MimeTypes
from datetime import date
from bcaw_utils import bcaw
import lucene

from bcaw import app
import bcaw_db
import bcaw_index
from sqlalchemy import *
from bcaw_userlogin_db import db_login, User, dbinit
###from runserver import db_login
from werkzeug.routing import BaseConverter
'''
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relation, sessionmaker
'''
'''
# searchable is commented outfor now
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_searchable import make_searchable
from sqlalchemy_utils.types import TSVectorType
from sqlalchemy.orm import relation, sessionmaker

from sqlalchemy_searchable import search


Base = declarative_base()

make_searchable()
'''

image_list = []
file_list_root = []
checked_list_dict = dict()

'''
NOTE: This function is a copy of bcawBroseImages, but with some changes (like
not initializing DB). Due to some issue with calling this routine from home(), 
and other route routines, the same code is inlined in those routines for now.
It needs to be changed by calling this routine instead.  

def bcawBrowse(db_init = True):
    global image_dir
    image_index = 0

    # Two lists are maintained: image_list: List of image names, 
    # image_db_list: List of the db_elements of all images. Each element is
    # a db-structure.
    # Since lists are declared globally, empty them before populating
    global image_list
    del image_list[:]
    global image_db_list
    del image_db_list [:]

    # Create the DB. FIXME: This needs to be called from runserver.py 
    # before calling run. That seems to have some issues. So calling from
    # here for now. Need to fix it.
    if db_init == True:
        session1 = bcaw_db.bcawdb()

    for img in os.listdir(image_dir):
        if img.endswith(".E01") or img.endswith(".AFF"):
            ## print img
            global image_list
            image_list.append(img)

            dm = bcaw()
            image_path = image_dir+'/'+img
            dm.num_partitions = dm.bcawGetPartInfoForImage(image_path, image_index)
            idb = bcaw_db.BcawImages.query.filter_by(image_name=img).first()
            image_db_list.append(idb)
            ## print("D: IDB: image_index:{}, image_name:{}, acq_date:{}, md5: {}".format(image_index, idb.image_name, idb.acq_date, idb.md5)) 
            image_index +=1
        else:
            continue
  
    # Render the template for main page.
    # print 'D: Image_list: ', image_list
    global num_images
    num_images = len(image_list)

    user = "Sign In"
    signup_out = "Sign Up"
    if 'email' in session:
      user = session['email']
      signup_out = "Sign Out"

    qform = QueryForm()

    return render_template('fl_temp_ext.html', image_list=image_list, np=dm.num_partitions, image_db_list=image_db_list, user=user, signup_out = signup_out, form=qform)

'''

#FIXME: The following line should be called in __init__.py once.
# Since that is not being recognized here, app.config.from_object is
# added here. This needs to be fixed.
app.config.from_object('bcaw_default_settings')
image_dir = app.config['IMAGEDIR']
dirFilesToIndex = app.config['FILES_TO_INDEX_DIR']
indexDir = app.config['INDEX_DIR']
num_images = 0
image_db_list = []

@app.route("/")

def bcawBrowseImages(db_init=True):
    global image_dir
    image_index = 0

    # Two lists are maintained: image_list: List of image names, 
    # image_db_list: List of the db_elements of all images. Each element is
    # a db-structure.
    # Since image_list is declared globally, empty it before populating
    global image_list
    del image_list[:]
    global image_db_list
    del image_db_list [:]

    # Create the DB. FIXME: This needs to be called from runserver.py 
    # before calling run. That seems to have some issues. So calling from
    # here for now. Need to fix it.
    if db_init == True:
        session1 = bcaw_db.bcawdb()

    for img in os.listdir(image_dir):
        if img.endswith(".E01") or img.endswith(".AFF"):
            ## print img
            global image_list
            image_list.append(img)

            dm = bcaw()
            image_path = image_dir+'/'+img
            dm.num_partitions = dm.bcawGetPartInfoForImage(image_path, image_index)
            idb = bcaw_db.BcawImages.query.filter_by(image_name=img).first()
            image_db_list.append(idb)
            ## print("D: IDB: image_index:{}, image_name:{}, acq_date:{}, md5: {}".format(image_index, idb.image_name, idb.acq_date, idb.md5)) 

            # Now download the files in the image to build the indexes.
            # FIXME: For now, I am downloading all the text files. Going forward,
            # each file is indexed and once the index is appended to the existing
            # index list, is deleted. This way we don't have to make space for all the
            # files in all the images
            temp_root_dir = "/vagrant"
            for p in range(0, dm.num_partitions):
                # make the directory for this img and partition
                part_dir = str(temp_root_dir) + '/img'+str(image_index)+"_"+ str(p)
                ## print("Part Dir: ", part_dir)
                #os.makedir(part_dir)
                file_list_root, fs = dm.bcawGenFileList(image_path, image_index,
                                             int(p), '/')
                print("Calling bcawDnldRepo with root ", file_list_root)
                # NOTE: The following is under construction. Hence commented out.
                ####bcawDnldRepo(file_list_root, part_dir, image_index, p, image_path, '/')
            '''
                for item in file_list_root:
                    if item['isdir'] == True:
                        print("It is a DIR", item['name'])
                    else:
                        print("It is a FILE", item['name'])
            '''

            image_index +=1
        else:
            continue

    # Build lucene index for the files stored in

    print("Building Lucene Indexes for root {} dest :{}".format(dirFilesToIndex, indexDir))

    ##lucene.initVM(vmargs=['-Djava.awt.headless=true'])
    print 'lucene', lucene.VERSION

    bcaw_index.IndexFiles(dirFilesToIndex, indexDir)
  
    # Render the template for main page.
    # print 'D: Image_list: ', image_list
    global num_images
    num_images = len(image_list)

    user = "Sign In"
    signup_out = "Sign Up"
    if 'email' in session:
      user = session['email']
      signup_out = "Sign Out"

    qform = QueryForm()

    return render_template('fl_temp_ext.html', image_list=image_list, np=dm.num_partitions, image_db_list=image_db_list, user=user, signup_out = signup_out, form=qform)


def bcawDnldRepo(root_dir_list, root_dir_path, image_index, partnum, image_path, root_path):
    # NOTE:
    # This routine is used to download the contents of the image which are text based,
    # in order to use for indexing for search utility. It is still under construction
    # since we need to figure out a way where we can download one file at a time,
    # build its index, append to the existing index and delete the file before
    # downloading another.
        print("Root dir list: ",root_path, len(root_dir_list),   root_dir_list)
        num_elements = len(root_dir_list)
        dm = bcaw()
        #root_path = '/'
        new_path = root_path
        for item in root_dir_list:
            if item['isdir'] == True:
                print("It is a Directory", item['name'])
                if item['name'] == '.' or item['name'] == '..':
                    continue
                new_path = new_path + '/'+ str(item['name'])

                # Call the function recursively
                item_root_dir = root_dir_path + '/' + str(item['name'])

                #new_path = root_path + '/' + str(item['name'])
                print("Calling func recursively with root - Newpath: ", item['name'], item, new_path)
                new_filelist_root, fs = dm.bcawGenFileList(image_path, image_index, partnum, new_path)
                bcawDnldRepo(new_filelist_root, item_root_dir, image_index, partnum, image_path, new_path)
            else:
                print("It is a File", item['name'])

def bcawGetImageIndex(image, is_path):
    global image_list
    if (is_path == True):
        image_name = os.path.basename(image_path)
    else:
        image_name = image
    global image_list
    for i in range(0, len(image_list)):
        if image_list[i] == image_name:
            return i
        continue
    else:
        print("Image not found in the list: ", image_name)

#
# Template rendering for Image Listing
#
@app.route('/image/<image_name>')
def image(image_name):
    # print("D: Partitions: Rendering Template with partitions for img: ", image_name)
    num_partitions = bcaw.num_partitions_ofimg[str(image_name)]
    part_desc = []
    image_index =  bcawGetImageIndex(image_name, is_path=False)
    for i in range(0, num_partitions):
        ## print("D: part_disk[i={}]={}".format(i, bcaw.partDictList[image_index][i]))
        part_desc.append(bcaw.partDictList[image_index][i]['desc'])

    return render_template('fl_img_temp_ext.html',
                            image_name=str(image_name),
                            num_partitions=num_partitions,
                            part_desc=part_desc)

@app.route('/image/metadata/<image_name>')
def image_psql(image_name):
    ## print("D: Rendering DB template for image: ", image_name)

    image_index =  bcawGetImageIndex(image_name, is_path=False)

    '''
    return render_template("db_image_template.html", 
                           image_name = image_name,
                           image=image_db[int(image_index)])
    '''
    return render_template("db_image_template.html", 
                           image_name = image_name,
                           image=image_db_list[image_index])

#
# Template rendering for Directory Listing per partition
#
@app.route('/image/<image_name>/<image_partition>')
def root_directory_list(image_name, image_partition):
    print("D: Files: Rendering Template with files for partition: ",
                            image_name, image_partition)
    image_index = bcawGetImageIndex(str(image_name), False)
    dm = bcaw()
    image_path = image_dir+'/'+image_name
    file_list_root, fs = dm.bcawGenFileList(image_path, image_index,
                                             int(image_partition), '/')
    ## print("\nRendering template fl_part_temp_ext.html: ", image_name, image_partition, file_list_root)
    return render_template('fl_part_temp_ext.html',
                           image_name=str(image_name),
                           partition_num=image_partition,
                           file_list=file_list_root)

# FIXME: Retained for possible later use
def stream_template(template_name, **context):
    #print("In stream_template(): ", template_name)
    app.update_template_context(context)
    t = app.jinja_env.get_template(template_name)
    rv = t.stream(context)
    rv.enable_buffering(5)
    return rv


#
# Template rendering when a File is clicked
#
@app.route('/image/<image_name>/<image_partition>', defaults={'filepath': ''})
@app.route('/image/<image_name>/<image_partition>/<path:filepath>')

def file_clicked(image_name, image_partition, filepath):
    print("\nFile_clicked: Rendering Template for subdirectory or contents of a file: ",
          image_name, image_partition, filepath)

    # Strip the digits after the last "-" from filepath to get inode
    new_filepath, separater, inode = filepath.rpartition("-") 

    print("D: Inode Split of file-name: new_filepath={}, sep:{}, inode:{} ".format\
            (new_filepath, separater, inode)) 
    if separater == "-":
        filepath = new_filepath

    # print("D: Files: Rendering Template for subdirectory or contents of a file: ",
          ## image_name, image_partition, path)
    
    image_index = bcawGetImageIndex(str(image_name), False)
    image_path = image_dir+'/'+image_name

    file_name_list = filepath.split('/')
    file_name = file_name_list[len(file_name_list)-1]

    # print "D: File_path after manipulation = ", path

    # To verify that the file_name exsits, we need the directory where
    # the file sits. That is if tje file name is $Extend/$RmData, we have
    # to look for the file $RmData under the directory $Extend. So we
    # will call the TSK API fs.open_dir with the parent directory
    # ($Extend in this example)
    temp_list = filepath.split("/")
    temp_list = file_name_list[0:(len(temp_list)-1)]
    parent_dir = '/'.join(temp_list)

    ## print("D: Invoking TSK API to get files under parent_dir: ", parent_dir)

    # Generate File_list for the parent directory to see if the
    dm = bcaw()
    file_list, fs = dm.bcawGenFileList(image_path, image_index,
                                        int(image_partition), parent_dir)

    # Look for file_name in file_list
    for item in file_list:
        print("D: item-name={} slug_name={} file_name={} item_inode={} ".format\
            (item['name'], item['name_slug'], file_name, item['inode']))

        # NOTE: There is an issue with recognizing filenames that have spaces.
        # All the characters after the space are chopped off at the route. As a
        # work-around a "slug" name is maintained in the file_list for each such
        # file. In order to recognize and map the chopped version of a file , the
        # file name is appended by its inode number. So when it gets here, a file
        # with a real name "Great Lunch.txt" will look like: "Great_Lunch.txt-xxx"
        # where xxx is the inode number. (Underscore is used to replace the blank
        # just for getting an idea on the file name. What is really used to recognize
        # the file is the inode.
        # Another issue is with the downloader not recognizing the spaces.
        #
        real_file_name = file_name
        if item['name_slug'] != "None" and item['inode'] == int(inode) :
            print("D >> Found a slug name ",item['name'], item['name_slug'])
            #file_name =  item['name_slug'].replace("%20", " ")
            # NOTE: Even the downloader doesn't like spaces in files. To keep
            # the complete name of the file, spaces are replaced by %20. The name
            # looks ugly, but till a cleaner solution is found, this is the best
            # fix.
            file_name =  item['name_slug']
            real_file_name = item['name_slug'].replace("%20", " ")

            print("D: real_file_name: {} slug_name={} ".format(real_file_name, file_name))

        if item['name'] == real_file_name:
            print("D : File {} Found in the list: ".format(file_name))
            break
    else:
        print("D: File_clicked: File {} not found in file_list".format(file_name))
        # FIXME: Should we abort it here?

    if item['isdir'] == True:
        # We will send the file_list under this directory to the template.
        # So calling once again the TSK API ipen_dir, with the current
        # directory, this time.
        ## filepath = filepath.replace(' ', '_')
        file_list, fs = dm.bcawGenFileList(image_path, image_index,
                                        int(image_partition), filepath)
        # Generate the URL to communicate to the template:
        with app.test_request_context():
            url = url_for('file_clicked', image_name=str(image_name), image_partition=image_partition, filepath=filepath )

        '''
        ############ Work under progress
        #If user has signed in, see if there is config info
        if 'email' in session:
          email = session['email']
          try:
            if checked_list_dict[email] != None:
              print("THERE IS STUFF IN CONFIG ", checked_list_dict[email])
              ##for item in checked_list_dict[email]:
                  ##print("Querying ", item)
                  ##qry = BcawDfxmlInfo.query.filter_by(image_name=image_name AND fo_filename=
            else:
              print("CHECKED LIST is empty")
          else:
        ############
        '''
        '''
        if 'email' in session:
            # get config_list
        '''

        print (">> Rendering template with URL: ", url)
        return render_template('fl_dir_temp_ext.html',
                   image_name=str(image_name),
                   partition_num=image_partition,
                   filepath=filepath,
                   file_list=file_list,
                   ##email = email,
                   ##checked_list=checked_list_dict[email],
                   url=url)

    else:
        print(">> Downloading File: ", real_file_name)
        # It is an ordinary file
        f = fs.open_meta(inode=item['inode'])
    
        # Read data and store it in a string
        offset = 0
        size = f.info.meta.size
        BUFF_SIZE = 1024 * 1024

        total_data = ""
        while offset < size:
            available_to_read = min(BUFF_SIZE, size - offset)
            data = f.read_random(offset, available_to_read)
            if not data:
                # print("Done with reading")
                break

            offset += len(data)
            total_data = total_data+data 
            # print "Length OF TOTAL DATA: ", len(total_data)
           

        ###file_new = "'" + real_file_name + "'"
        mime = MimeTypes()
        mime_type, a = mime.guess_type(file_name)
        generator = (cell for row in total_data
                for cell in row)
        return Response(stream_with_context(generator),
                        mimetype=mime_type,
                        headers={"Content-Disposition":
                                    "attachment;filename=" + file_name })
        '''
        return render_template('fl_filecat_temp_ext.html',
        image_name=str(image_name),
        partition_num=image_partition,
        file_name=file_name,
        contents=str(data))
        #contents = data.decode("utf-8"))
        '''
@app.route('/testdb')
def testdb():
    '''
    if db_login.session.query("1").from_statement("SELECT 1").all():
        return 'It works.'
    else:
        return 'Something is broken.'
    '''
    if bcaw_db.db.session.query("1").from_statement("SELECT 1").all():
        return 'It works.'
    else:
        return 'Something is broken.'

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    ##session = dbinit()
    form = SignupForm()

    if request.method == 'POST':
        if form.validate() == False:
            return render_template('fl_signup.html', form=form)
        else:
            newuser = User(form.firstname.data, form.lastname.data, form.email.data, form.password.data)
            db_login.session.add(newuser)
            db_login.session.commit()

            session['email'] = newuser.email

            ##return "[1] Create a new user [2] sign in the user [3] redirect to the user's profile"
            return redirect(url_for('profile'))

    elif request.method == 'GET':
        return render_template('fl_signup.html', form=form)

@app.route('/home')
def home():
    #return render_template('fl_profile.html')
    # NOTE: There is code duplication here. Merge the folowing with bcawBrowse
    # and call from both places (root and /home)
    ####return(bcawBrowse(db_init=False))

    global image_dir
    image_index = 0

    # Since image_list is declared globally, empty it before populating
    global image_list
    del image_list[:]
    global image_db_list
    del image_db_list [:]

    # Create the DB. FIXME: This needs to be called from runserver.py 
    # before calling run. That seems to have some issues. So calling from
    # here for now. Need to fix it.
    for img in os.listdir(image_dir):
        if img.endswith(".E01") or img.endswith(".AFF"):
            ## print img
            global image_list
            image_list.append(img)

            dm = bcaw()
            image_path = image_dir+'/'+img
            dm.num_partitions = dm.bcawGetPartInfoForImage(image_path, image_index)
            idb = bcaw_db.BcawImages.query.filter_by(image_name=img).first()
            image_db_list.append(idb)
            ## print("D: IDB: image_index:{}, image_name:{}, acq_date:{}, md5: {}".format(image_index, idb.image_name, idb.acq_date, idb.md5)) 
            image_index +=1
        else:
            continue
  
    # Render the template for main page.
    # print 'D: Image_list: ', image_list
    global num_images
    num_images = len(image_list)

    user = "Sign In"
    signup_out = "Sign Up"
    if 'email' in session:
      user = session['email']
      signup_out = "Sign Out"

    qform = QueryForm()

    return render_template('fl_temp_ext.html', image_list=image_list, np=dm.num_partitions, image_db_list=image_db_list, user=user, signup_out = signup_out, form=qform)

@app.route('/about')
def about():
    return render_template('fl_profile.html')

@app.route('/contact')
def contact():
    return render_template('fl_profile.html')

@app.route('/profile')
def profile():
  if 'email' not in session:
    return redirect(url_for('signin'))
 
  user = User.query.filter_by(email = session['email']).first()
 
  if user is None:
    return redirect(url_for('signin'))
  else:
    return render_template('fl_profile.html')

@app.route('/config', methods=['POST','GET'])
def config():
  config_list = ['filename', 'po', 'sectsize', 'blksize']
  if 'email' not in session:
    return redirect(url_for('config'))

  user = User.query.filter_by(email = session['email']).first()
 
  if user is None:
    return redirect(url_for('signin'))
  else:
    config
    return render_template('fl_config.html', 
                   config_list=config_list,
                   num_config_items=str(len(config_list)))
    
@app.route('/fl_process_confinfo.html',  methods=['POST','GET'])
def fl_process_confinfo():
    checked_list = request.form.getlist('config_item')
    print("Checked File list: ", checked_list)

    '''
    email = session['email']

    checked_list_dict[email] = checked_list
    '''

    # FIXME: This needs to be made persistent
    if 'email' in session:
        email = session['email']
        print("D: Adding Email ", email)
        checked_list_dict[email] = checked_list

    print("D: Checked DICT: ", checked_list_dict)


    return render_template('fl_process_confinfo.html', checked_list=checked_list)
    #return render_template('fl_process_confinfo.html')

@app.route('/signin', methods=['GET', 'POST'])
def signin():
  form = SigninForm()
  if request.method == 'POST':
    if form.validate() == False:
      return render_template('fl_signin.html', form=form)
    else:
      session['email'] = form.email.data
      return redirect(url_for('profile'))
  elif request.method == 'GET':
    return render_template('fl_signin.html', form=form)

@app.route('/signout')
def signout():
  if 'email' not in session:
    return redirect(url_for('signin'))

  session.pop('email', None)
  return redirect(url_for('home'))
'''
def bcaw_query(db, phrase):
    query = db.session.query()
    query = search(query, phrase)

    print("D: ", query.first().name)
'''

@app.route('/query', methods=['GET', 'POST'])
def query():
    form = QueryForm()
    if request.method == 'POST':
        search_result_file_list = []
        search_result_image_list = []
        searched_phrase = form.search_text.data.lower()

        search_result_list, search_type = form.searchDfxmlDb()
        if search_type == "filename":
            if search_result_list == None:
                print "No search results for ", searched_phrase
                num_results = 0
            else:
                i = 0
                # Note; For now, two separae lists are maintained - one for filename
                # and another for the corresponding image. If we need more than two
                # columns to display then it makes sense to have an array if structues
                # instead of 2 separate lists.
                for list_item in search_result_list:
                    #search_result_file_list[i] = list_item.fo_filename
                    search_result_file_list.append(list_item.fo_filename)
                    search_result_image_list.append(list_item.image_name)
                    ## print("search_result_file_list[{}] = {}, img: {} ".format(i, search_result_file_list[i], list_item.image_name))
                    i += 1
                print "D: query:Result:len: {}, file: {} ".format(len(search_result_list), search_result_list[0].fo_filename)

                num_results = len(search_result_list)
        else: # search type is "Contents"
            if search_result_list == None:
                print "No search results for ", searched_phrase
                num_results = 0
            else:
                print "search result list: ", search_result_list
                num_results = len(search_result_list)
                search_result_file_list = search_result_list

        if search_result_list == None:
            print "Query: searchDfxmlDb FAILED "
            num_results = 0
        else:
            print "Searched for ", searched_phrase

        user = "Sign In"
        signup_out = "Sign Up"
        if 'email' in session:
          user = session['email']
          signup_out = "Sign Out"

        print (">> Rendering template with URL:  ")
        return render_template('fl_search_results.html',
                                searched_phrase=searched_phrase,
                                num_results=num_results,
                                search_result_file_list=search_result_file_list,
                                search_result_image_list=search_result_image_list,
                                user=user, signup_out = signup_out, form=form)
                                                    
            
    elif request.method == 'GET':
        return render_template('fl_query.html', form=form)
        

    ##query = bcaw_query(BcawDfxmlInfo, phrase) 
    #engine = create_engine('postgresql://vagrant:vagrant@localhost/bca_db')

    '''
    engine = create_engine('postgresql://vagrant:vagrant@localhost/bca_db')

    #Base.metadata.create_all(engine)
    db_login.Model.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    query1 = session.query(bcaw_db.BcawDfxmlInfo)

    print("QUERY PASSED ")
    #print(query1)

    ####query = search(query1, 'astronaut.jpg', vector=bcaw_db.BcawDfxmlInfo.fo_filename)
    query = search(query1, 'astronaut.jpg', vector=bcaw_db.BcawDfxmlInfo.fo_filename)

    print("query: ", query)


    print query.first()

    ####query = db_login.session.query()
    ####query = search(query, 'Email')

    #print("query.first.fo_filename : ", query.first().fo_filename)
    return render_template("fl_profile.html")
    '''

# FIXME: This is never called (since we run runserver.py)
# Remove once confirmed to be deleted
if __name__ == "__main__":
    dm = bcaw()
    bcaw_db.bcawdb()
    app.run()
