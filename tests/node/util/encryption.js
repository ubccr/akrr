var crypto = require('crypto');
var assert = require('assert');
var validation = require('./validation.js')

var ENCRYPTION = function (options) {

    this.DEFAULT_ALGORITHM = 'aes-256-ctr';
    this.DEFAULT_PASSWORD = this._generateDefaultPassword();
    this.DEFAULT_ENCODING = 'utf8';
    this.DEFAULT_OUTPUT = 'hex';

    var options = options || {}

    var hasAlgorithms = validation.hasA(options, 'algorithm');
    var hasPassword = validation.hasA(options, 'password');
    var hasEncoding = validation.hasA(options, 'encoding');
    var hasOutput = validation.hasA(options, 'output');


    this.algorithm = hasAlgorithms ? options.algorithm : this.DEFAULT_ALGORITHM;
    this.password = hasPassword ? options.password : this.DEFAULT_PASSWORD;
    this.encoding = hasEncoding ? options.encoding : this.DEFAULT_ENCODING;
    this.output = hasOutput ? options.output : this.DEFAULT_OUTPUT;
};

ENCRYPTION.prototype._generateDefaultPassword = function () {
    var time = (Math.floor(Math.random() * 1024) + new Date().getTime() ).toString();
    var start = time.length - 8;
    var end = Math.max(start + 8, time.length);
    return time.slice(start, end);
}


ENCRYPTION.prototype.encrypt = function (text, algorithm, password, encoding, output) {

    validation.existsAndIsA(text, String, true);

    var algorithm = validation.existsAndIsAOr(algorithm, String, this.algorithm);
    var password = validation.existsAndIsAOr(password, String, this.password);
    var encoding = validation.existsAndIsAOr(encoding, String, this.encoding);
    var output = validation.existsAndIsAOr(output, String, this.output);

    var cipher = crypto.createCipher(algorithm, password);
    var result = cipher.update(text, encoding, output);
    result += cipher.final(output);

    return result;
}

ENCRYPTION.prototype.decrypt = function (text, algorithm, password, encoding, output) {
    validation.existsAndIsA(text, String, true);

    var algorithm = validation.existsAndIsAOr(algorithm, String, this.algorithm);
    var password = validation.existsAndIsAOr(password, String, this.password);
    var encoding = validation.existsAndIsAOr(encoding, String, this.encoding);
    var output = validation.existsAndIsAOr(output, String, this.output);

    var decipher = crypto.createDecipher(algorithm, password);
    var result = decipher.update(text, output, encoding);
    result += decipher.final(encoding);

    return result;
}

module.exports = ENCRYPTION;
