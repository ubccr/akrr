// REQUIRE: the AKRR API library.
var API = require('./util/api.js');

describe('AKRR REST API', function () {
    var valid_api = new API({
        verbose: true,
        password: 'Ohf4oZ6w'
    });

    var invalid_api = new API({
        verbose: true,
        password: 'blahblah'
    });

    describe('get_token route', function () {

        it("should accept valid auth information and return a token.", function (done) {
            var token_id = 'valid_auth';
            valid_api.get_token(token_id, function (error, token) {
                expect(error).toBe(null);
                expect(token).toBeDefined();
                done();
            });
        });

        it("should *not* accept invalid auth information.", function (done) {
            var token_id = 'invalid_auth';
            invalid_api.password = 'blahblah';

            invalid_api.get_token(token_id, function (error, token) {
                expect(error).toBeDefined();
                expect(error.response).toBeDefined();
                expect(error.response.statusCode).toBeDefined();
                expect(error.response.statusCode).toEqual(401);
                expect(token).toBeNull();
                done();
            });
        });

        it("should return the same token if the same key is requested.", function (done) {
            var token_id = "repeat_auth";

            valid_api.get_token(token_id, function (error, token) {
                expect(error).toBeNull();
                expect(token).toBeDefined();

                valid_api.get_token(token_id, function (error, next_token) {
                    expect(error).toBeNull();
                    expect(next_token).toBeDefined();
                    expect(next_token).toEqual(token);
                    done();
                });
            });
        });
    });


});
