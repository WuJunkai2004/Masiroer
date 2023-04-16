import json
import re
import requests

import sys

class cookies:
    __cookie__ = {}
    def __init__(self):
        pass
    def __setattr__(self, name, value):
        self.__cookie__[name] = value
    def __getattr__(self, name):
        return self.__cookie__[name]
    def get_all(self):
        return self.__cookie__


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
        data = self.translate_variables(self.rule['data']['dataset'], args, kwargs)
        base, info = self.translate_request()
        text = requests.request(*base, **info).text
        return self.translate_content(text, self.rule['response'])

    def translate_variables(self, dataset, args, kwargs):
        result = {}
        for index in range(len(args)):
            result[ dataset[index]['name'] ] = args[index]
        result.update(kwargs)
        for item in dataset:
            pass#验证是否含有全部必须变量
        return result

    def translate_content(self, data, method):
        result = {}
        for index in method['order']:
            if(method[index]['type']=='return'):
                 return result[ method[index]['refer'] ]
            if(method[index]['type']=="regex"):
                result[index] = re.search(method[index]["rule"], data).group()
            elif(method[index]['type']=='find'):
                result[index] = re.findall(method[index]["rule"], data)
            elif(method[index]["type"]=='func'):
                if(method[index]["func"]=='json'):
                    result = json.loads(data)
                pass #若有其他需求
            elif(method[index]['type']=='range'):
                result[index] = []
                for sub in result[ method[index]['refer'] ]:
	                result[index].append( self.translate_content(sub, method[index]['rule']) )
            else:
                raise RuntimeError('unknown type: {}'.format(index))
        return result


class categories:
    def __init__(self, load):
        for files in load:
            self.setattr(files['name'], executor('instruct\\' + files['path']))


with open('config.json', 'r') as fin:
    _config = json.load(fin)

forum = categories( _config['forum'] )
users = categories( _config['users'] )
books = categories( _config['books'] )
lists = categories( _config['lists'] )
myself  = categories( _config['myself'] )