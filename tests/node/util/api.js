/**
 * Default module for working with the AKRR REST API
 **/
process.env.NODE_TLS_REJECT_UNAUTHORIZED = "0";

var assert = require('assert');
var request = require('request');
var fs = require('fs');
var validation = require('./validation.js');
var CRYPTO = require('./encryption.js');


var DEFAULT_PROTOCOL = 'https://';
var DEFAULT_HOST = 'appkernel.ccr.buffalo.edu';
var DEFAULT_PORT = 8091;
var DEFAULT_USER = 'rw';
var DEFAULT_API_ROOT = '/api/v1/'
var DEFAULT_CIPHER = 'aes256';

var API = function (options) {

    var options = options || {};

    var hasProtocol = validation.hasA(options, 'protocol');
    var hasHost = validation.hasA(options, 'host');
    var hasPort = validation.hasA(options, 'port');
    var hasUser = validation.hasA(options, 'user');
    var hasPassword = validation.hasA(options, 'password');
    var hasApiRoot = validation.hasA(options, 'api_root');
    var hasCipher = validation.hasA(options, 'cipher');
    var hasVerbose = validation.hasA(options, 'verbose');

    this.protocol = hasProtocol ? options.protocol : DEFAULT_PROTOCOL;
    this.host = hasHost ? options.host : DEFAULT_HOST;
    this.port = hasPort ? options.port : DEFAULT_PORT;
    this.user = hasUser ? options.user : DEFAULT_USER;
    this.password = hasPassword ? options.password : null;
    this.api_root = hasApiRoot ? options.api_root : DEFAULT_API_ROOT;
    this.cipher = hasCipher ? options.cipher : DEFAULT_CIPHER;
    this.verbose = hasVerbose ? options.verbose : false;


    this.url = this.protocol + this.host + ":" + this.port + this.api_root;
    this.tokens = {};
};

API.prototype.get = function (token, url, data) {

};

API.prototype.put = function (token, url, data) {

};

API.prototype.post = function (token, url, data) {

};

API.prototype.delete = function (token, url, data) {

};

API.prototype.save_auth = function (file, callback) {
    if (validation.isA(file, String)) {

    }
};

API.prototype.load_auth = function (file, callback) {
    if (file && typeof(file) === 'string') {
        try {
            fs.readFile(file, {
                encoding: 'utf8'
            }, function (err, data) {
                if (err) throw err;
                var crypto = new CRYPTO();
                try {
                    var decrypted = crypto.decrypt(data);
                    var decryptedJson = JSON.decode(decrypted);

                }
                // ATTEMPT: to decrypt the document.
                // ATTEMPT: to decode the json document.
                // SNAG:    the password / encryption algorithm
                // ATTEMPT: to decrypt the auth information.
                // SET: the auth information.
                callback(null, true);
            });
        } catch (err) {
            console.log('Unable to read from: ' + file);
            callback(err, false);
        }
    } else {
        callback(null, false);
    }
};

/**
 * Used to forcibly eject a token from the local cache of tokens.
 *
 * @param key_id the key
 */
API.prototype.eject_token = function (key) {
    if (key && this.tokens[key]) {
        this.tokens[key] = null;
    }
};

/**
 * Attempt to retrieve a new authentication / authorization token from the AKRR
 * REST API.
 * @param callback will be called with the result of the 'get_token' operation.
 *                 the signature of which is: error, token
 */
API.prototype.get_token = function (key, callback) {
    var self = this;
    assert.equal(
        typeof(key),
        'string',
        "The argument 'key_id' must be of type 'string'."
    );

    // IF: we already have this token then return it...
    if (key in this.tokens) {
        callback(null, this.tokens[key]);
    } else {
        // ELSE: go ahead and attempt to retrieve it...
        var callback = callback || function () {
            };

        var options = {
            method: 'GET',
            uri: this.url + 'token',
            auth: {
                user: this.user,
                password: this.password,
                sendImmediately: false
            },
            sslStrict: false
        };

        request(options,
            function (error, response, body) {
                if (error || response.statusCode != 200) {
                    callback({
                        error: error,
                        response: response
                    }, null);
                } else {
                    var token = null;
                    var json = JSON.parse(body);
                    if (json && json.data && json.data.token) {
                        token = json.data.token;
                        self.tokens[key] = token;
                        callback(null, token);
                    }
                }
            });
    }
}

module.exports = API;
