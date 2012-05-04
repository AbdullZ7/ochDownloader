import sys
from operator import itemgetter

#PIL library.
import Image

def color_rank(img):
    img = img.convert("P")
    his = img.histogram()
    values = {}
    
    for i in range(256):
      values[i] = his[i]
      
    for j, k in sorted(values.items(), key=itemgetter(1), reverse=True)[:10]:
      print j, k
  
def convert_to_greyscale(img):
    if img.mode != 'L':
        img = img.convert('L')
    return img

def clean_noise(img, allowed):
    img2 = img.load()
    w, h = img.size

    for x in xrange(w):
        for y in xrange(h):
            if img2[x, y] == 255: continue
                # no point in processing white pixels since we only want to remove black pixel
            count = 0

            try:
                if img2[x-1, y-1] != 255: count += 1
                if img2[x-1, y] != 255: count += 1
                if img2[x-1, y + 1] != 255: count += 1
                if img2[x, y + 1] != 255: count += 1
                if img2[x + 1, y + 1] != 255: count += 1
                if img2[x + 1, y] != 255: count += 1
                if img2[x + 1, y-1] != 255: count += 1
                if img2[x, y-1] != 255: count += 1
            except:
                pass

        # not enough neighbors are dark pixels so mark this pixel
            # to be changed to white
            if count < allowed:
                img2[x, y] = 1

    # second pass: this time set all 1's to 255 (white)
    for x in xrange(w):
        for y in xrange(h):
            if img2[x, y] == 1: img2[x, y] = 255

    return img

def keep_range_color(img, range_limit):
    img = img.convert("P")
    img2 = Image.new("P", img.size, 255)

    img = img.convert("P")

    temp = {}

    for x in range(img.size[1]):
      for y in range(img.size[0]):
        pix = img.getpixel((y, x))
        temp[pix] = pix
        if pix < range_limit: # these are the numbers to get
          img2.putpixel((y, x), 0)

    return img2


if __name__ == "__main__":
    pass


