import sys
import pdb
import os
import urllib
from PIL import Image 
import webapp2

CACHE_PATH="/shared/photo-cache"
IMAGE_PATH="/shared/photo"
LEN_IMAGE_PATH=len(IMAGE_PATH)
IMAGE_URL="http://microserver.lan/photo"
CACHE_PATH="/shared/photo-cache"
LEN_CACHE_PATH=len(CACHE_PATH)
VIEWER_URL_PATH="/photo-viewer"
VIEWER_URL="http://microserver.lan" + VIEWER_URL_PATH
EXTENSION_MAP = {'gif':'png','tif':'png'}
MAX_SIZE = 150

def path_to_viewer_url(path):
        if path.startswith(IMAGE_PATH):
                return VIEWER_URL + urllib.quote(path[LEN_IMAGE_PATH:],'/')
        raise ValueError


def path_to_url(path):
	if path.startswith(IMAGE_PATH):
		return IMAGE_URL + urllib.quote(path[LEN_IMAGE_PATH:],'/')
	if path.startswith(CACHE_PATH):
                return CACHE_PATH + urllib.quote(path[LEN_CACHE_PATH:],'/')
	pdb.set_trace()
	raise ValueError

def path_to_cache(path):
	if path.startswith(IMAGE_PATH):
		(path1,ext) = os.path.splitext(path[LEN_IMAGE_PATH:])
		cached_path = CACHE_PATH + path1 + '.' + EXTENSION_MAP.get(ext.lower()[1:],'jpg')
		if not os.path.exists(cached_path):
			try:
				image = Image.open(path)
				image.thumbnail((MAX_SIZE,MAX_SIZE))
			except (OSError, IOError):
				image = Image.new("RGB",(MAX_SIZE,MAX_SIZE),"#ff0000")
			dir = os.path.dirname(cached_path)
			if not os.path.exists(dir):
				os.makedirs(dir)
			image.save(cached_path)
                return cached_path
        raise ValueError

def images_directories_and_other(path, image_extensions=(".jpg",".jpeg",".gif",".png",'tif')):
	image_extensions_lower = tuple((extension.lower() for extension in image_extensions))
	images=[]
	directories=[]
	other=[]
	try:
		names=os.listdir(path)
	except OSError:
		names = []
	for name in names:
		name_lower = name.lower()
		full_path = os.path.join(path,name)
		if os.path.isfile(full_path) and any((name_lower.endswith(extension) for extension in image_extensions_lower)):
			images.append((name,full_path))
		elif os.path.isdir(full_path):
			directories.append((name,full_path))
		else:
			other.append((name,full_path))
	images.sort(key=lambda x:x[0])
	directories.sort(key=lambda x:x[0])
	other.sort(key=lambda x:x[0])
	return (images, directories, other)

class HelloWebapp2(webapp2.RequestHandler):
    def get(self, url_path):
	#pdb.set_trace()
	start_path = IMAGE_PATH + urllib.unquote(url_path)
	real_path = os.path.realpath(start_path)
	# Check that we're allowed to access this area
	if not real_path.startswith(CACHE_PATH) and not real_path.startswith(IMAGE_PATH):
		raise OSError
	(images,directories,other)=images_directories_and_other(start_path)
	self.response.write("Images<br/>")
	for (name,full_path) in images:
		self.response.write("<a href='%s'><img src='%s' alt='%s'/></a>" % (path_to_url(full_path),path_to_url(path_to_cache(full_path)),name))
	self.response.write("<br/>")
	self.response.write("Directories<br/>")
	for (name,full_path) in directories:
                self.response.write("<a href='%s'>%s</a><br/>" % (path_to_viewer_url(full_path),name))
	self.response.write("Other<br/>")
        for (name,full_path) in other:
                self.response.write("<a href='%s'>%s</a><br/>" % (path_to_url(full_path),name))

app = webapp2.WSGIApplication([
    ('(/.*)', HelloWebapp2),
], debug=True)

def main():
    from paste import httpserver
    httpserver.serve(app, host='127.0.0.1', port='8080')

if __name__ == '__main__':
    main()
