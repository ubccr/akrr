var CRYPTO = require('./util/encryption.js');

describe('AKRR Test Encryption Functionality', function () {

    var DEFAULT_INPUT = 'Hello World';

    it('should be able to successfully encrypt plain text.', function (done) {
        var crypto = new CRYPTO();
        var encrypted = crypto.encrypt(DEFAULT_INPUT);

        expect(encrypted).toBeDefined();
        expect(encrypted).not.toEqual(DEFAULT_INPUT);
        done();
    });

    it('should be able to decrypt encrypted text, given the settings are the same.', function (done) {
        var crypto = new CRYPTO();
        var encrypted = crypto.encrypt(DEFAULT_INPUT);

        expect(encrypted).toBeDefined();
        expect(encrypted).not.toEqual(DEFAULT_INPUT);

        var decrypted = crypto.decrypt(encrypted);

        expect(decrypted).toBeDefined();
        expect(decrypted).toEqual(DEFAULT_INPUT);

        done();
    });

    it('should not be able to decrypt encrypted output from another encryption instance.', function (done) {
        var original = new CRYPTO();


        var first = original.encrypt(DEFAULT_INPUT);

        expect(first).toBeDefined();
        expect(first).not.toEqual(DEFAULT_INPUT);

        var nextTime = new CRYPTO();

        var second = nextTime.decrypt(first);

        expect(second).toBeDefined();
        expect(second).not.toEqual(DEFAULT_INPUT);
        done();
    });

    it('should throw an error if null is passed as the text to be encrypted.', function (done) {
        var crypto = new CRYPTO();
        try {
            crypto.encrypt(null);
        } catch (error) {
            expect(error).toBeDefined();
            done();
        }
    });

    it('should throw an error if undefined is passed as the text to be encrypted', function (done) {
        var crypto = new CRYPTO();
        try {
            crypto.encrypt(undefined);
        } catch (error) {
            expect(error).toBeDefined();
            done();
        }
    });

    it('should throw an error if a number is passed as the text to be encrypted', function (done) {
        var crypto = new CRYPTO();
        try {
            crypto.encrypt(12345);
        } catch (error) {
            expect(error).toBeDefined();
            done();
        }
    });

    it('should throw an error if an object is passed as the text to be encrypted', function (done) {
        var crypto = new CRYPTO();
        try {
            crypto.encrypt({});
        } catch (error) {
            expect(error).toBeDefined();
            done();
        }
    });

    it('should throw an error if a function is passed as the text to be encrypted', function (done) {
        var crypto = new CRYPTO();
        try {
            crypto.encrypt(function () {
            });
        } catch (error) {
            expect(error).toBeDefined();
            done();
        }
    });

    it('should throw an error if null is passed as the text to be decrypted.', function (done) {
        var crypto = new CRYPTO();
        try {
            crypto.decrypt(null);
        } catch (error) {
            expect(error).toBeDefined();
            done();
        }
    });

    it('should throw an error if undefined is passed as the text to be decrypted', function (done) {
        var crypto = new CRYPTO();
        try {
            crypto.decrypt(undefined);
        } catch (error) {
            expect(error).toBeDefined();
            done();
        }
    });

    it('should throw an error if a number is passed as the text to be decrypted', function (done) {
        var crypto = new CRYPTO();
        try {
            crypto.decrypt(12345);
        } catch (error) {
            expect(error).toBeDefined();
            done();
        }
    });

    it('should throw an error if an object is passed as the text to be decrypted', function (done) {
        var crypto = new CRYPTO();
        try {
            crypto.decrypt({});
        } catch (error) {
            expect(error).toBeDefined();
            done();
        }
    });

    it('should throw an error if a function is passed as the text to be decrypted', function (done) {
        var crypto = new CRYPTO();
        try {
            crypto.decrypt(function () {
            });
        } catch (error) {
            expect(error).toBeDefined();
            done();
        }
    });
});