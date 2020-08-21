import os
import uuid
from PIL import Image
from PIL import ImageOps
from pprint import pformat as pf
import subprocess
import shlex
from flask_login import (LoginManager, current_user, login_required,
                         login_user, logout_user, UserMixin, AnonymousUserMixin,
                         confirm_login, fresh_login_required)
import boto3

import config_s3


s3 = boto3.client('s3')
xenon_bucket = 'mendeleev-xenon-prod'
xenon_camera_path = 'xenon/cameras/'

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

def get_s3_sub_dirs(root_dir):
    print('root_dir: ' + root_dir)
    if not root_dir.endswith('/'):
        root_dir = root_dir + '/'
    s3_path = ['Select']
    result = s3.list_objects(Bucket=xenon_bucket, Prefix=root_dir, Delimiter='/')
    if 'CommonPrefixes' in result:
        for o in result.get('CommonPrefixes'):
            print ('sub folder : ' + o.get('Prefix'))
            s3_path.append(o.get('Prefix').replace(config_s3.py['mediadir'], '')[:-1])
        return s3_path
    else:
        return []


def get_s3_file_list(get_path):
    if not get_path.startswith(config_s3.py['mediadir']):
        get_path = config_s3.py['mediadir'] + get_path 
    if not get_path.endswith('/'):
        get_path = get_path + '/'
    elif get_path.endswith('//'):
        get_path = get_path[:-1]

    file_list = []
    s3_result =  s3.list_objects_v2(Bucket=xenon_bucket, Prefix=get_path, Delimiter = "/")
    if 'Contents' not in s3_result:
        return []

    for key in s3_result['Contents']:
        file_list.append(key['Key'])

    while s3_result['IsTruncated']:
        continuation_key = s3_result['NextContinuationToken']
        s3_result = s3.list_objects_v2(Bucket=xenon_bucket, Prefix=get_path, Delimiter="/", ContinuationToken=continuation_key)
        for key in s3_result['Contents']:
            file_list.append(key['Key'])
    # return file_list

    path_file_list = []
    for f in file_list:
        suffix = f.lower().split('.')[1]
        if suffix not in config_s3.py['supported_files']:
            continue
        
        path_file_list.append(f)

    return path_file_list


def return_creds(role_arn):
    session_name = str(uuid.uuid3(namespace=uuid.NAMESPACE_DNS,
                       name=os.path.splitext(os.path.basename(__file__))[0]))
    
    sts_client = boto3.client('sts')
    resp = sts_client.assume_role(
        RoleArn=role_arn,
        RoleSessionName=session_name)

    if 200 <= resp['ResponseMetadata']['HTTPStatusCode'] < 300:
        return resp['Credentials']
    else:
        return None



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

        tree_path = path.replace(config_s3.py['mediadir'], '')
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
                if suffix not in config_s3.py['supported_files']:
                    continue

                ftype = None
                if suffix in config_s3.py['supported_images']:
                    ftype = "img"

                    # create thumbs if necessary
                    if not os.path.isfile(path+'thumbs/'+f):
                        resizePic(
                            path + f, (config_s3.py['thumbres'], config_s3.py['thumbres'])).save(path + 'thumbs/' + f)

                    # create websize if necessary
                    if not os.path.isfile(path+'web/'+f):
                        resizePic(
                            path + f, (config_s3.py['webres'], config_s3.py['webres'])).save(path + 'web/' + f)

                elif suffix in config_s3.py['supported_videos']:
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
            subdirs.append(subdir.replace(config_s3.py['mediadir'], ''))

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
        dirs[path.replace(config_s3.py['mediadir'], '')] = {
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
    dirs = scanDir(config_s3.py['mediadir'])
    return dirs.keys()


##### upload path validation #######
def isValidMediaPath(path):
    if not path.startswith(config_s3.py['mediadir']):
        return False
    else:
        return True
