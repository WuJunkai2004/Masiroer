import json as _json
import re   as _re
import sys  as _sys

import requests as _requests


def _search_solo(pattern, string):
    get = _re.search(pattern, string)
    if(get):
        return get.group()
    return ''


def _search_mult(pattern, string):
    gets = []
    for item in _re.finditer(pattern, string):
        gets.append( item.group() )
    return gets


class _cookies:
    __files__   = []
    def __init__(self, file = None):
        self.__cookie__ = {}
        if(file):
            self.__files__.append(file)
        if(self.__files__):
            self.start(self.__files__[-1])

    def __setitem__(self, name, value):
        self.__cookie__[name] = value
        self.__handle__.write( '{}\t{}\n'.format(name, value) )

    def __getitem__(self, name):
        return self.__cookie__[name]
    
    def __del__(self):
        if( hasattr(self, '__handle__') ):
            self.__handle__.close()
    
    def start(self, file):
        with open(file, 'r') as fin:
            for line in fin.readlines():
                self.__cookie__.__setitem__( *line[:-1].split('\t', 1) )
        self.__handle__ = open(file, 'a+')
    
    def gets(self):
        return self.__cookie__

    def puts(self, get):
        for name in get.keys():
            self.__cookie__[name] = get[name]

    def clean(self):
        pass


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
            with open(self.file, 'r', encoding='UTF-8') as fin:
                self.rule = _json.load(fin)
        except FileNotFoundError:
            print("Error: File not found")
        except _json.JSONDecodeError:
            print('Error: Invalid json data in file')
        else:
            self.is_load = True

    def __call__(self, *args, **kwargs):
        if(not self.is_load):
            self.load()
        data = self.translate_variables(self.rule['data']['dataset'], args, kwargs)
        base, info = self.translate_request( data )

        request = _requests.request(*base, **info)

        if(self.rule['isSaveCookie']):
            self.cook().puts( request.cookies.get_dict() )

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
        _sys.stderr.write( str(base) )
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
            if(item['name'] not in result.keys()):
                if(item['required']):
                    raise AttributeError('The Attibution of {} is Required'.format(item['name']))
                if(not item["required"] and "defined" in item.keys()):
                    result[ item["name"] ] = item["defined"]
        return result

    def translate_content(self, data, method):
        result = {}
        for index in method['order']:
            if  ( method[index]['type'] == 'return' ):
                return result[ method[index]['refer'] ]
            if  ( method[index]['type'] == "regex"  ):
                result[index] = _search_solo(method[index]["rule"], data)
            elif( method[index]['type'] == 'find'   ):
                result[index] = _search_mult(method[index]["rule"], data)
            elif( method[index]["type"] == 'func'   ):
                if  ( method[index]["func"] == 'json' ):
                    result[index] = _json.loads(data)
                elif( method[index]["func"] == "code" ):
                    data = data.encode().decode("unicode_escape")
                elif( method[index]["func"] == "save" ):
                    with open("temp/temp.txt","w+") as fout:
                        fout.write(data)
            elif( method[index]['type'] == 'refer'  ):
                get = result
                for item in method[index]["rule"]:
                    get = get[item]
                result[index] = get
            elif( method[index]['type'] == 'range'  ):
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
    with open('config.json', 'r') as fin:
        return _json.load(fin)


_config = _load_config('config.json')

forum = _categories( _config['forum'] )
lists = _categories( _config['lists'] )

auth  = _categories( _config["auth"] )
user  = _categories( _config['user'] )
book  = _categories( _config['book'] )
self  = _categories( _config['self'] )