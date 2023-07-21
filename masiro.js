const axios = require("axios");
const fopen = require('fs');

axios.defaults.withCredentials = true;

var defined_cookie_file = "cookie.tmp";

const regex = {
    "hunt":(pattern, string)=>{
        let ans=string.match( RegExp(pattern) );
        if(ans)
            return ans[0];
        else   
            console.error(pattern+'\n'+string)
    },
    "seek":(pattern, string)=>{
        let ans = [],from = string.matchAll(RegExp(pattern, 'g'))
        for(let item of from)
            ans.push( item[0] );
        return ans;
    },
    "find":(pattern, string)=>{
        let ans = [],from = string.matchAll(RegExp(pattern, 'g'));
        for(let item of from)
            ans.push(item[0]);
        return ans;
    },
    "exist":(pattern, string)=>{
        return RegExp(pattern).exec(string) != null;
    }
}


function cookies(file = null){
    let cookie = {};
    let handle = null;
    if(!file){
        if(!defined_cookie_file)
            throw "Need a cookies file path";
        file = defined_cookie_file;
    }
    else{
        defined_cookie_file = file;
    }
    let data = fopen.readFileSync(file, 'utf8');
    let lines = data.split('\n');
    for (let line of lines) {
        if(line){
            const [name, value] = line.slice(0, -1).split('\t', 2);
            cookie[name] = value;
        }
    }
    handle = fopen.openSync(file, 'a+');
    return {
        "set_value":(name, value)=>{
            cookie[name] = value;
            fopen.writeSync(handle, `${name}\t${value}\n`);
        },
        "get_value":(name)=>{
            return cookie[name];
        },
        "gets":()=>{
            return cookie;
        },
        "puts":(get)=>{
            for (let name in get) 
                cookie[name] = get[name];
        },
        "encode":()=>{
            let lines = [];
            for(let name in cookie)
                lines.push(`${name}=${cookie[name]}`);
            return lines.join('; ');
        }
    }
}


async function requests(method, url, more){
    let config = more;
    config.url = url,config.method = method;
    let [text, cookies] = await axios(
        config
    ).then( response => {
        let data = response.data, cookie = response.headers['set-cookie'],real_cookie={};
        if(typeof data != "string")
            data = JSON.stringify(data);
        for(let lines of cookie){
            let line=lines.replace(/expires=.+?;/gi,'')
                          .replace(/Max-age=.+?;/gi,'')
                          .replace(/path=.+/gi,'')
                          .replace(/;/,'')
                          .trim();
            let [name, value] = line.slice(0, -1).split('=', 2);
            real_cookie[name] = value;
        }
        return [ data, real_cookie ];
    })
    return {
        "text":text,
        "cookies":cookies
    };
}


function executor(config_file, use_cookie = cookies){
    let is_load = false;
    let file = config_file;
    let rule = null;
    let cook = use_cookie;

    function load(){
        try {
            rule = JSON.parse( fopen.readFileSync(file, "utf8") );
            is_load = true;
        } catch (error) {
            console.log(error);
        }
    }

    function translate_request(data){
        let base =  [ ( rule.isWithDate && ["params"].indexOf(rule.data.method) == -1 )?"post":"get", rule.URL ];
        let info = {
            'headers' : {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
                'Accept':'*/*',
                'Accept-Language':'zh-CN,zh;q=0.9,en;q=0.8'
            }
        };
        if(rule.isWithData){
            switch(rule.data.method){
                case 'params':{
                    info.params = data;
                }break;
                case 'json':{
                    info.data = data;
                }break;
                default:{
                    throw "stop"
                }break;
            }
        }
        if(rule.isWithCookie){
            info.headers.cookie = cook().encode();
        }
        return [base, info];
    }
    function translate_variables(dataset, args){
        let result = {};
        for(let index in args)
            result[ dataset[index].name ] = args[index];
        for(let item of dataset){
            if( Object.keys(result).indexOf(item.name) == -1 ){
                if(item.required)
                    throw `AttributeError : The Attibution of ${item.name} is Required` ;
                if(!item.required && Object.keys(item).indexOf("defined") != -1)
                    result[ item.name ] = item.defined ;
            }
        }
        return result;
    }

    function translate_content(data, method){
        let result = {} ;
        for(let index of method.order){
            switch( method[index].type ){
                case "return":{
                    return result[ method[index].refer ]
                };

                case "regex":{
                    result[ index ] = regex[ method[index].func ]( method[index].rule, data )
                }break;

                case "func":{
                    switch (method[index].func ){
                        case "json":{
                            result[index] = JSON.parse(data);
                        }break;
                        case "code":{
                            console.error( "decode unicode" );
                        }break;
                        case "save":{
                            fopen.writeFileSync("temp/temp.txt", data, {
                                encoding:"utf8",
                                flag:"w+"
                            })
                        }break;
                        case "del":{
                            delete result[ method[index].refer ];
                        }break;
                    }
                }break

                case "refer":{
                    let get = result;
                    for(let item of method[index].rule)
                        get = get[item];
                    result[index] = get;
                }break;

                case "range":{
                    result[index] = [];
                    for(let sub of result[ method[index].refer ]){
                        result[index].push( translate_content(sub, method[index].rule) );
                    }
                }break;

                default:{
                    throw `[RuntimeError] : unknown type ${index}`;
                }
            }
        }

        console.log(result);

        for(let name in result)
            if( name.startsWith('temp') )
                delete result[ name ] ;

        return result;
    }

    return async function(...args){
        if(!is_load)
            load();
        let data = translate_variables(rule.data.dataset, args)
        let [base, info] = translate_request( data );
        let response = await requests(base[0], base[1], info);
        if(rule.isSaveCookie)
            cook().puts( response.cookies );
        return translate_content(response.text, rule.response);
    };
}


function categories(load){
    let executors = {}
    for(let index in load)
        executors[ load[index].name ] = executor('configure\\' + load[index].file);
    return executors;
}

const config = JSON.parse( fopen.readFileSync('config.json') );

const forum = categories(config.forum);
const lists = categories(config.lists);
const novel = categories(config.novel);

const auth  = categories(config.auth );
const user  = categories(config.user );
const self  = categories(config.self );

module.exports = {
    cookies,
    forum, lists, novel, 
    auth,  user,  self
};
