const axios = require("axios");
const fopen = require('fs');

axios.defaults.withCredentials = true;

var defined_cookie_file = null


function cookies(file = null){
    let cookie = {}
    let handle = null;
    if(!file){
        if(!defined_cookie_file){
            throw "Need a cookies file path";
        }
        file = defined_cookie_file;
    }
    else{
        defined_cookie_file = file;
    }
    return {
        "start":()=>{
            const data = fopen.readFileSync(file, 'utf8');
            const lines = data.split('\n');
            for (let line of lines) {
                const [name, value] = line.slice(0, -1).split('\t', 2);
                cookie[name] = value;
            }
            handle = fopen.openSync(file, 'a+');
        },
        "set_value":(name, value)=>{
            cookie[name] = value;
            fopen.writeSync(this.__handle__, `${name}\t${value}\n`);
        },
        "get_value":(name)=>{
            return cookie[name];
        },
        "gets":()=>{
            return cookie;
        },
        "puts":(get)=>{
            for (let name in get) {
                if (get.hasOwnProperty(name)) {
                    cookie[name] = get[name];
                }
            }
        }
    }
}


function executor(config_file, use_cookie = cookies){
    let is_load = false;
    let file = config_file;
    let rule = null;
    let cook = use_cookie

    function load(){
        try {
            rule = JSON.parse( fopen.readFileSync(file, "utf8") );
            is_load = true;
        } catch (error) {
            console.log(error);
        }
    }

    function translate_request(data){
        let base =  [ ( rule.isWithDate && ["params"].indexOf(rule.data.method) == -1 )?"POST":"GET", rule.URL ];
        let info = {
            'headers' : {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
                'Accept':'*/*',
                'Accept-Language':'zh-CN,zh;q=0.9,en;q=0.8'
            }
        };
        if(rule.isWithDate){
            info[ rile.data.method ] = data;
        }
        if(rule.isWithCookie){
            info.cookies = cook().gets();
        }
        return [base, info];
    }
    function translate_variables(dataset, args){
        let result = {};
        for(let index in args){
            result[ dataset[index].name ] = args[index];
        }
        for(let index in dataset){
            null;
        }
        return result;
    }

    function translate_content(data, method){
        return null;
    }

    async function requests(method, url, more){
        return {
            "text":null,
            "cookies":{"one":"11111"}
        }
    }

    return async function(...args){
        if(!is_load){
            load();
        }
        let data = translate_variables(rule.data.dataset, args)
        let [base, info] = translate_request( data );
        console.log(base)
        console.log(info)
        let response = await requests(base[0], base[1], info)
        if(rule.isSaveCookie){
            cook().puts( response.cookies );
        }
        return translate_content(response.text, rule.response);
    };
}


function categories(load){
    let executors = {}
    for(let index in load){
        executors[ load[index].name ] = executor('configure\\' + load[index].file)
    }
    return executors
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