import enum
import os
import secrets
from flask import current_app
from PIL import Image

class TasksBasedOnDates:
    def __init__(self, date, tasks):
        self.date = date
        self.tasks = tasks

class ColorPickOptions:
    def __init__(self, value, id):
        self.value = value
        self.id = id

class Colors(enum.Enum):
    blue = 'bg-primary'
    
def save_picture(form_picture):
    # we need to create random names for each picture so that no 2 pics can have same name
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_new_name = random_hex + f_ext
    # get the location to store the image
    picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_new_name)
    # save the picture after resizing
    output_size = (125,125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_new_name
