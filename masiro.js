const axios = require("axios")


class Cookies {
    constructor(file) {
        this.__cookie__ = {};
        if (file) {
            this.constructor.__files__.push(file);
        }
        if (this.constructor.__files__.length > 0) {
            this.start(this.constructor.__files__[this.constructor.__files__.length - 1]);
        }
    }

    setValue(name, value) {
        this.__cookie__[name] = value;
        this.__handle__.write(`${name}\t${value}\n`);
    }

    getValue(name) {
        return this.__cookie__[name];
    }

    __del__() {
        if (this.hasOwnProperty('__handle__')) {
            this.__handle__.close();
        }
    }

    start(file) {
        const fs = require('fs');
        const data = fs.readFileSync(file, 'utf8');
        const lines = data.split('\n');
        for (let line of lines) {
            const [name, value] = line.split('\t', 2);
            this.__cookie__.__setitem__(name, value);
        }
        this.__handle__ = fs.openSync(file, 'a+');
    }

    gets() {
        return this.__cookie__;
    }

    puts(get) {
        for (let name in get) {
            if (get.hasOwnProperty(name)) {
                this.__cookie__[name] = get[name];
            }
        }
    }

    clean() {
        // Add your clean-up logic here
    }
}

Cookies.__files__ = [];

module.exports = Cookies;