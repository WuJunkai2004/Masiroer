import json as _json
import re   as _re
import sys  as _sys

import requests as _requests


class _cookies:
    __cookie__ = {}
    def __setitem__(self, name, value):
        self.__cookie__[name] = value
    def __getitem__(self, name):
        return self.__cookie__[name]
    def gets(self):
        return self.__cookie__
    def puts(self, gets):
        for name in gets.keys():
            self.__cookie__[name] = gets[name]
    def load(self, file):
        with open(file, 'r') as fin:
            self.puts( _json.load(fin) )
    def dump(self, file):
        with open(file, 'w+') as fout:
            _json.dump(self.__cookie__, fout)

class defined_cookies(_cookies):
    pass


class _executor:
    def __init__(self, config_file, use_cookie = defined_cookies):
        self.is_load = False
        self.file = config_file
        self.rule = None
        self.cook = use_cookie

    def load(self):
        try:
            with open(self.file, 'r') as fin:
                self.rule = _json.load(fin)
        except FileNotFoundError:
            print("Error: File not found")
        except _json.JSONDecodeError:
            print('Error: Invalid _json data in file')
        else:
            self.is_load = True

    def __call__(self, *args, **kwargs):
        if(not self.is_load):
            self.load()
        data = self.translate_variables(self.rule['data']['dataset'], args, kwargs)
        base, info = self.translate_request( data )

        request = _requests.request(*base, **info)

        print(request.text)

        if(self.rule['isSaveCookie']):
            self.cook().puts(request.cookies.get_dict())

        return self.translate_content(request.text, self.rule['response'])
    
    def translate_request(self, data):
        base = ["POST"if(self.rule['isWithData'] and self.rule['data']['method'] not in ('params'))else'GET', self.rule['URL'] ]
        info = {
            'headers' : {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
                'Accept':'*/*',
                'Accept-Language':'zh-CN,zh;q=0.9,en;q=0.8'
            }
        }
        print(base,file = _sys.stderr)
        if(self.rule['isWithData']):
            info[ self.rule['data']['method'] ] = data
        if(self.rule['isWithCookie']):
            info['cookies'] = self.cook().gets()
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
                result[index] = _re.search(method[index]["rule"], data).group()
            elif(method[index]['type']=='find'):
                result[index] = _re.findall(method[index]["rule"], data)
            elif(method[index]["type"]=='func'):
                if(method[index]["func"]=='_json'):
                    result[index] = _json.loads(data)
            elif(method[index]['type']=='range'):
                result[index] = []
                for sub in result[ method[index]['refer'] ]:
                    result[index].append( self.translate_content(sub, method[index]['rule']) )
            else:
                raise RuntimeError('unknown type: {}'.format(index))
        return result


class _categories:
    def __init__(self, load):
        for files in load:
            setattr(self, files['name'], _executor('configure\\' + files['file']))


def _load_config(file):
    with open('config._json', 'r') as fin:
        return _json.load(fin)


_config = _load_config('config._json')

forum = _categories( _config['forum'] )
lists = _categories( _config['lists'] )

auth  = _categories( _config["auth"] )
user  = _categories( _config['user'] )
book  = _categories( _config['book'] )
self  = _categories( _config['self'] )