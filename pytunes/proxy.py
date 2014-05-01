""" Tool for proxying images and resizing if needed """
import os
import hashlib
import pytunes
import imghdr
import logging
from cherrypy.lib.static import serve_file
from urllib2 import Request, urlopen
try:
    import Image
    PIL = True
except ImportError:
    try:
        from PIL import Image
        PIL = True
    except ImportError:
        PIL = False
logger = logging.getLogger('pytunes.proxy')

def get_image(url, height=None, width=None, opacity=100, auth=None):
    """ Load image form cache if possible, else download. Resize if needed """
    opacity = float(opacity)
    logger.debug("Get Image: %s, Height: %s, Width: %s, Opacity: %s" % (url, height, width, opacity))

    # Create image directory if it doesnt exist
    imgdir = os.path.join(pytunes.DATADIR, 'images/')
    if not os.path.exists(imgdir):
        logger.debug("Creating image directory at " + imgdir)
        os.makedirs(imgdir)

    # Create a hash of the path to use as filename
    imghash = hashlib.md5(url).hexdigest()

    # Set filename and path
    image = os.path.join(imgdir, imghash)

    # If there is no local copy of the original
    if not os.path.isfile(image):
        logger.debug("No local image found for " + image + ". Downloading")
        download_image(url, image, auth)

    # Check if resize is needed
    if (height and width) or (opacity < 100):
        if PIL:
            # Set filename for resized file
            resized = image + '_w' + width + '_h' + height + '_o' + str(opacity)
            # If there is no local resized copy
            if not os.path.isfile(resized):
                resize_image(image, height, width, opacity, resized)
            # Serve the resized file
            image = resized
        else:
            logger.error("Can't resize when PIL is missing on system!")
            if (opacity < 100):
                image = os.path.join(pytunes.RUNDIR, 'interfaces/default/img/fff_20.png')
    # Load file from disk
    imagetype = imghdr.what(image)
    if imagetype is not None:
        return serve_file(path=image, content_type='image/' + imagetype)

def download_image(url, dest, auth=None):
    """ Download image and save to disk """
    logger.debug("Downloading image from " + url + " to " + dest)
    try:
        request = Request(url)
        if (auth):
            request.add_header("Authorization", "Basic %s" % auth)
        with open(dest, "wb") as local_file:
            local_file.write(urlopen(request).read())
        logger.debug("Finished downloading image from " + url + " to " + dest)
    except Exception:
        logger.error("Failed downloading image from " + url + " to " + dest)
        pass

def resize_image(img, height, width, opacity, dest):
    """ Resize image, set opacity and save to disk """
    size = int(width), int(height)
    imagetype = imghdr.what(img)
    try:
        im = Image.open(img)
        im = im.resize(size, Image.ANTIALIAS)
    except:
        logger.error("Failed resizing image: %s" % img)
        return
    # Apply overlay if opacity is set
    opacity = float(opacity)
    if (opacity < 100):
        enhance = opacity / 100
        # Create white overlay image
        overlay = Image.new('RGB', size, '#FFFFFF')
        # apply overlay to resized image
        im = Image.blend(overlay, im, enhance)
    if imagetype == 'jpeg':
        im.save(dest, 'JPEG', quality=95)
    im.save(dest, imagetype)
    return dest
