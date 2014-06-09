'''
Created on May 27, 2014

@author: Vincent Ketelaars
'''
import collections
import os
import logging
from PIL import Image
from src.pytesser import pytesser
from PIL import ImageEnhance
from src.general.constants import TESSERACT_ON

logger = logging.getLogger(__name__)

CAPTCHA_FILENAME = "captcha"
CAPTCHA_EXT = ".jpg"
CAPTCHA_WORDS_FILES = ["movies.txt", "actors.txt", "actresses.txt"]
        
def convert_captcha_to_string(pic, directory):
    path = os.path.join(directory, CAPTCHA_FILENAME + CAPTCHA_EXT)
    with open(path, "wb") as f:
        f.write(pic) 
        logger.info("Wrote content of size %d to %s", len(pic), path)
    path4 = enhance_image(path)
    logger.debug("Enhanced image at %s", path4)
    image = Image.open(path4)
    parsed = pytesser.image_to_string(image).strip()
    logger.debug("Pytesser found %s", parsed)
    return correct(parsed.lower())

def enhance_image(path):
    directory = os.path.dirname(path)
    im = Image.open(path)
    nx, ny = im.size
    im2 = im.resize((int(nx*5), int(ny*5)), Image.BICUBIC)
    path2 = os.path.join(directory, CAPTCHA_FILENAME + "2" + CAPTCHA_EXT) 
    im2.save(path2)
    enh = ImageEnhance.Contrast(im)
    enh.enhance(1.3)
     
    imgx = Image.open(path2)
    imgx = imgx.convert("RGBA")
    pix = imgx.load()
    for y in xrange(imgx.size[1]):
        for x in xrange(imgx.size[0]):
            if pix[x, y] >= (150, 150, 150, 255):
                pix[x, y] = (255, 255, 255, 255)
            else:
                pix[x, y] = (0, 0, 0, 255)
    path3 = os.path.join(directory, "bw.gif")
    imgx.save(path3, "GIF")
    original = Image.open(path3)
    bg = original.resize((116, 56), Image.NEAREST)
    path4 = os.path.join(directory, "input-NEAREST.tif")
    bg.save(path4)
    return path4

if TESSERACT_ON: # Very computationally expensive.. Only do it if it is necessary
    # http://norvig.com/spell-correct.html
    NWORDS = collections.defaultdict(lambda: 1)
    for words_file in CAPTCHA_WORDS_FILES:
        with open(words_file, "r") as f:
            for l in f.readlines():
                t, o = l.split(",")
                NWORDS[t] = int(o.strip())

alphabet = 'abcdefghijklmnopqrstuvwxyz ' # include space

def edits1(word):
    splits     = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    deletes    = [a + b[1:] for a, b in splits if b]
    transposes = [a + b[1] + b[0] + b[2:] for a, b in splits if len(b)>1]
    replaces   = [a + c + b[1:] for a, b in splits for c in alphabet if b]
    inserts    = [a + c + b     for a, b in splits for c in alphabet]
    return set(deletes + transposes + replaces + inserts)

def guess_by_characters_and_length(words_dict, word, distance=1, length=0):
    words = {}
    for w, count in words_dict.iteritems():
        if abs(len(word) - len(w)) <= length:
            for i in range(distance):
                if word[i] != w[i] or word[-1 - i] != w[-1 - i]:
                    break
            else:
                words[w] = count
    return words

def guess_iterate(word):
    i = 1
    words_dict = NWORDS
    while True:
        result = guess_by_characters_and_length(words_dict, word, i, 0)
        if len(result) == 0:
            break
        else:
            words_dict = result
        i += 1
    return set(words_dict)

def known_edits2(word):
    return set(e2 for e1 in edits1(word) for e2 in edits1(e1) if e2 in NWORDS)

def known(words): 
    return set(w for w in words if w in NWORDS)

def correct(word):
    candidates = known([word]) or known(edits1(word)) or known_edits2(word) or guess_iterate(word) or set([word])
    return max(candidates, key=NWORDS.get)