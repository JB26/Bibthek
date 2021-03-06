'''Genarate thumbs using PIL'''
from PIL import Image

def gen_thumbs(thumbnail):
    '''Genarate thumb and save it'''
    size = (350, 350)
    infile = thumbnail[:-10]
    im = Image.open(infile)
    im.thumbnail(size, Image.ANTIALIAS)
    im.save(thumbnail, "JPEG", quality=50)
    return thumbnail
