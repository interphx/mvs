import os
import uuid
import mimetypes
from hashlib import md5
from flask import url_for

from project import db

from .model import Upload

# TODO
STATIC_FILES_LOCATION = 'static'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'bmp', 'pdf'}

MIME_TO_TYPE = {
	'image/jpeg': 'image',
	'image/png': 'image',
	'image/gif': 'image',
	'image/bmp': 'image',
	'application/pdf': 'document',
	'application/x-pdf': 'document'
}

MIME_TO_EXT = {
	'image/jpeg': 'jpg',
	'image/png': 'png',
	'image/gif': 'gif',
	'image/bmp': 'bmp',
	'application/pdf': 'pdf',
	'application/x-pdf': 'pdf'
}

class FileTypeNotAllowed(Exception): pass

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def upload_file(file, description='', role='other', author_id=None):
	if not allowed_file(file.filename):
		raise FileTypeNotAllowed()

	mime = mimetypes.guess_type(file.filename)[0]
	type = MIME_TO_TYPE[mime]
	ext = MIME_TO_EXT[mime]

	blob = file.read()
	hash = md5(blob).hexdigest()

	duplicate = Upload.query.filter_by(hash=hash).first()
	if duplicate:
		return duplicate

	unique_name = str(uuid.uuid4()).replace('-', '')
	filename = unique_name + '.' + ext
	filepath = STATIC_FILES_LOCATION + '/uploads/' + filename	

	url_path = url_for('static', filename='uploads/' + filename)

	file.seek(0)
	file.save(filepath)

	upload = Upload(
		author_id=author_id,
		type=type,
		role=role,
		hash=hash,
		mime=mime,
		description=description,
		file_path=filepath,
		url=url_path
	)

	try:
		db.session.add(upload)
		db.session.commit()
	except:
		db.session.rollback()
		raise

	return upload