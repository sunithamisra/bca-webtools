##from flask import Flask
##app = Flask(__name__)
#IMAGEDIR = '/home/bcadmin/disk_images'
IMAGEDIR = '/vagrant/disk-images'
DELETED_FILES = True
INDEX_DIR = "/vagrant/lucene_index"
FILES_TO_INDEX_DIR = "/vagrant/files_to_index"
# FILESEARCH_DB: If set, searches for the filenames in the DB as opposed to
# searching the index
FILESEARCH_DB = True
# FILE_IDEXDIR is the directory where the index for filename search is stored.
FILENAME_INDEXDIR = "/vagrant/filenames_to_index"
