import json
import re
import requests

import sys

class executor:
    def __init__(self, config_file):
        self.is_load = False
        self.file = config_file
        self.rule = ''

    def load(self):
        try:
            with open(self.file, 'r') as fin:
                self.rule = json.load(fin)
        except FileNotFoundError:
            print("Error: File not found")
        except json.JSONDecodeError:
            print('Error: Invalid JSON data in file')
        else:
            self.is_load = True

    def __call__(self, *args, **kwargs):
        if(not self.is_load):
            self.load()
        if(self.rule["isWithData"]):
            pass


class categories:
    def __init__(self, load):
        for files in load:
            self.setattr(files['name'], executor(files['path']))


def analyze(data, method):
    result = {}
    for index in method['order']:
        if(method[index]['return']=='return'):
             return result[ method[index]['refer'] ]
        if(method[index]['type']=="regex"):
            result[index] = re.search(method[index]["rule"], data).group()
        elif(method[index]['type']=='find'):
            result[index] = re.findall(method[index]["rule"], data)
        elif(method[index]["type"]=='func'):
            if(method[index]["func"]=='json'):
                result[index] =json.loads(data)
        elif(method[index]['type']=='range'):
            result[index] = []
            for sub in result[ method[index]['refer'] ]:
	            result[index].append( analyze(sub, method[index]['rule']) )
        else:
            raise RuntimeError('unknown type: {}'.format(index))
    return result

with open('config.json', 'r') as fin:
    _config = json.load(fin)

forum = categories( _config['forum'] )
users = categories( _config['users'] )
books = categories( _config['books'] )
lists = categories( _config['lists'] )
myself = categories( _config['myself'] )
