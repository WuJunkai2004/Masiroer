import json
import re
import requests

import sys

class _cookies:
    __cookie__ = {}
    def __init__(self):
        pass
    def __setitem__(self, name, value):
        self.__cookie__[name] = value
    def __getitem__(self, name):
        return self.__cookie__[name]
    def get_all(self):
        return self.__cookie__
    def save(self, gets):
        for name in gets.keys():
            self[name] = gets[name]

class defined_cookies(_cookies):
    pass


class executor:
    def __init__(self, config_file, use_cookie = defined_cookies):
        self.is_load = False
        self.file = config_file
        self.rule = None
        self.cook = use_cookie

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
        print(self.rule)
        data = self.translate_variables(self.rule['data']['dataset'], args, kwargs)
        base, info = self.translate_request( data )

        request = requests.request(*base, **info)

        print(request.text)

        self.cook().save(request.cookies.get_dict())
        return self.translate_content(request.text, self.rule['response'])
    
    def translate_request(self, data):
        base = ["POST"if(self.rule['isWithData'])else'GET', self.rule['URL'] ]
        info = {
            'headers' : {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
        }
        if(self.rule['isWithData']):
            data_type = {"urlencoded":"data",
                         }[self.rule['data']['method']]
            info[data_type] = data
        if(self.rule['isWithCookie']):
            info['cookies'] = self.cook().get_all()
        return base, info

    def translate_variables(self, dataset, args, kwargs):
        result = {}
        for index in range(len(args)):
            result[ dataset[index]['name'] ] = args[index]
        result.update(kwargs)
        for item in dataset:
            if(item['required'] and item['name'] not in result.keys()):
                raise AttributeError('The Attibution of {} is Required'.format(item['name']))
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
            setattr(self, files['name'], executor('configure\\' + files['file']))


with open('config.json', 'r') as fin:
    _config = json.load(fin)

forum   = categories( _config['forum'] )
users   = categories( _config['users'] )
books   = categories( _config['books'] )
lists   = categories( _config['lists'] )
myself  = categories( _config['myself'] )