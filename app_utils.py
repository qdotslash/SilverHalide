import os
from PIL import Image
from PIL import ImageOps
from pprint import pformat as pf
import subprocess
import shlex
from flask_login import (LoginManager, current_user, login_required,
                         login_user, logout_user, UserMixin, AnonymousUserMixin,
                         confirm_login, fresh_login_required)

import config


class User(UserMixin):
    def __init__(self, name, id, pwhash, active=True):
        self.name = name
        self.id = id
        self.active = active
        self.pwhash = pwhash

    def is_active(self):
        return self.active


class Anonymous(AnonymousUserMixin):
    name = u"Anonymous"


##### create user objects ######

def get_users(userfile):
    '''
    load users from file
    '''
    users = {}
    n = 1
    with open(userfile) as f:
        for line in f.readlines():
            if line != '\n' and not line.startswith('#'):
                u = line.strip('\n').split(' ')
                users[n] = User(u[0], n, u[1])
    n = + 1
    return users


##### image resizing ######

def resizePic(pic, res,):
    i = Image.open(pic)
    i.thumbnail(res, Image.ANTIALIAS)
    return i


def sub_dirs(root_dir):
    """
    Scans root_dir for sub directories
    """
    if root_dir.endswith('/'):
        root_dir = root_dir[:-1]
    sub_dirs_with_paths = [f.path for f in os.scandir(root_dir) if f.is_dir()]
    sub_dirs = ['Select ID']
    for sd in sub_dirs_with_paths:
        if 'web' in sd.lower():
            continue
        if 'thumbs' in sd.lower():
            continue
        sub_dirs.append(sd.replace(config.py['mediadir'], ''))

    return sub_dirs


def get_file_list(get_path):
    if not get_path.startswith(config.py['mediadir']):
        get_path = config.py['mediadir'] + get_path 
    if not get_path.endswith('/'):
        get_path = get_path + '/'
    get_dir = get_path.replace(config.py['mediadir'], '')  # used for path_file_list not scandir
    file_list = [f.name for f in os.scandir(get_path) if f.is_file()]
    path_file_list = []
    for f in file_list:
        suffix = f.lower().split('.')[1]
        if suffix not in config.py['supported_files']:
            continue
        
        path_file_list.append(get_path + f)

    return path_file_list


##### directory scanner ######
def scanDir(get_path):
    """
    Scans subdirs and files in path and returns a list 
    of dict for each directory.

    example for these dicts:
    {'files':[{'name': 'filename.jpg', 'date': mtime }, 'subdirs':[], 'dir':'']}
    """
    dirs = {}
    dir_tree = {}
    for d in os.walk(get_path):
        # path=d[0].encode('utf-8')
        path = d[0]

        # ignore thumb and web sub-dirs
        if not (path.endswith('thumbs') or path.endswith('web')):

            if not path.endswith('/'):
                path = path + '/'
        else:
            continue

        tree_path = path.replace(config.py['mediadir'], '')
        print('Path: ' + tree_path)
        dir_tree = nest_dict({tree_path: tree_path}, os.path.sep, dir_tree)
        
        # create thumb and web sub-dirs if needed
        for sub in ['thumbs', 'web']:
            if not os.path.isdir(path+sub):
                os.mkdir(path+sub)


        # create empty file list for current dir
        files = []

        if get_path == path:
            # save stats for every file in dict
            for f in d[2]:
                suffix = f.lower().split('.')[1]
                if suffix not in config.py['supported_files']:
                    continue

                ftype = None
                if suffix in config.py['supported_images']:
                    ftype = "img"

                    # create thumbs if necessary
                    if not os.path.isfile(path+'thumbs/'+f):
                        resizePic(
                            path + f, (config.py['thumbres'], config.py['thumbres'])).save(path + 'thumbs/' + f)

                    # create websize if necessary
                    if not os.path.isfile(path+'web/'+f):
                        resizePic(
                            path + f, (config.py['webres'], config.py['webres'])).save(path + 'web/' + f)

                elif suffix in config.py['supported_videos']:
                    ftype = "vid"

                    # create video thumbnail
                    if not os.path.isfile(path+'thumbs/'+f+'.png'):
                        command = 'ffmpeg -y -i ' + path + f + \
                            ' -vframes 1 -ss 2 ' + path + 'thumbs/' + f + '.png'
                        proc = subprocess.Popen(shlex.split(command))

                files.append(
                    {'name': f, 'mtime': os.path.getmtime(path+'/'+f), 'type': ftype})

        # remove thumb and web from subdir listing
        try:
            d[1].remove('web')
        except:
            pass
        try:
            d[1].remove('thumbs')
        except:
            pass

        # empty list of subdirs
        subdirs = []

        for subdir in d[1]:
            subdirs.append(subdir.replace(config.py['mediadir'], ''))

        # handle dir without files
        if len(files) == 0:
            dirthumb = 'img/fallback.jpg'
        else:
            if files[0]['name'][-3:] == 'mp4':
                dt = files[0]['name']+'.png'
            else:
                dt = files[0]['name']
            dirthumb = path[7:] + 'thumbs/' + dt

        # save dir stats in dict
        dirs[path.replace(config.py['mediadir'], '')] = {
                'subdirs': subdirs, 'files': files, 'dirthumb': dirthumb}
    return dirs, dir_tree


# code to conert dict into nested dict
def nest_dict(dict1, delim, nested):
    for k, v in dict1.items():
        # for each key call method split_rec which
        # will split keys to form recursively
        # nested dictionary
        split_rec(delim, k, v, nested)
    return nested


def split_rec(delimeter, k, v, out):

    # splitting keys in dict
    # calling_recursively to break items on '_'
    k, *rest = k.split(delimeter, 1)
    if rest:
        split_rec(delimeter, rest[0], v, out.setdefault(k, {}))
    else:
        if k:
            out[k] = v
        else:
            if v:
                out['_path'] =  v


##### get all mediadir subdirs #######
def getSubdirs():
    subs = []
    dirs = scanDir(config.py['mediadir'])
    return dirs.keys()


##### upload path validation #######
def isValidMediaPath(path):
    if not path.startswith(config.py['mediadir']):
        return False
    else:
        return True
