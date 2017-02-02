from django.utils import timezone
from datetime import timedelta
from cStringIO import StringIO
from PIL import Image


def nextDayOfWeekToDatetime(dt, day_of_week):
    days_of_week = ['mon', 'tue', 'wed', 'thur', 'fri', 'sat', 'sun']
    while dt.weekday() != days_of_week.index(day_of_week):
        dt+=timedelta(days=1)
    return dt

def cropImageToSquare(image):
    file_jpgdata = StringIO(image)
    image = Image.open(file_jpgdata)
    w, h = image.size
    half_width = w / 2
    half_height = h / 2
    if w >= h:
        image = image.crop((half_width-half_height, 0, half_width+half_height, h))
    else:
        image = image.crop((0, half_height - half_width, w, half_height + half_width))
    return image

def cropImageByAspectRatio(image, aspect_width, aspect_height):
    assert(aspect_height>=aspect_width) # Only implemented to work for portrait orientation
    file_jpgdata = StringIO(image)
    image = Image.open(file_jpgdata)
    w, h = image.size
    half_width = w/2
    cropped_w = (float(h) * float(aspect_width))/float(aspect_height)
    half_cropped_width = int(cropped_w) / 2
    image = image.crop((half_width - half_cropped_width, 0, half_width + half_cropped_width, h))
    return image

def cropImage(image, startx, starty, endx, endy):
    file_jpgdata = StringIO(image)
    image = Image.open(file_jpgdata)
    image = image.crop((startx, starty, endx, endy))
    return image

def cropImageByAspectRatioAndCoordinates(image, startx, starty, endx, endy, aspect_width, aspect_height):
    w, h = image.size
    centerx = (endx+startx) / 2
    centery = (endy+starty) / 2
    y_increment = (float(aspect_height) / float(aspect_width)) / 2.0
    x_increment = 1.0 / 2.0
    start_cropx = centerx
    end_cropx = centerx
    start_cropy = centery
    end_cropy = centery
    # Gradually increase bounds by aspect_ratio. Stop when there is no more room to increase
    while True:
        if (start_cropx - x_increment < 1 and end_cropx + x_increment > w) or\
            (start_cropy - y_increment < 1 and end_cropy + y_increment > h):
            break

        if (start_cropx - x_increment) >= 1:
            start_cropx -= x_increment
            if (end_cropx + x_increment >= w):
                start_cropx -= x_increment

        if (end_cropx + x_increment) <= w:
            end_cropx += x_increment
            if (start_cropx - x_increment <= 1):
                end_cropx += x_increment

        if(start_cropy - y_increment) >= 1:
            start_cropy -= y_increment
            if(end_cropy + y_increment) >= h:
                start_cropy -= y_increment
        if(end_cropy + y_increment) <= h:
            end_cropy += y_increment
            if(start_cropy - y_increment) <= 1:
                end_cropy += y_increment
    image = image.crop((start_cropx, start_cropy, end_cropx, end_cropy))
    return image