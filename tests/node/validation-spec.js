var validations = require('./util/validation.js');

describe('The Validation utility', function () {

    var SAMPLE_TEXT = 'Hello World';
    var SAMPLE_NUMBER = 123456;
    var SAMPLE_FUNCTION = function () {
    };
    var NULL = null;
    var UNDEFINED = undefined;
    var EMPTY_TEXT = '';
    var FLOATING_NUMBER = 12.34;

    var SAMPLE_OBJECT = {
        string: SAMPLE_TEXT,
        empty: EMPTY_TEXT,
        number: SAMPLE_NUMBER,
        floating: FLOATING_NUMBER,
        fun: SAMPLE_FUNCTION,
        none: NULL,
        undef: UNDEFINED
    };


    describe('The isA function', function () {

        it('should be able to correctly identify a string.', function (done) {
            var result = validations.isA(SAMPLE_TEXT, String);
            expect(result).toBeDefined();
            expect(result).toEqual(true);
            done();
        });

        it('should be able to correctly identify an empty string.', function (done) {
            var result = validations.isA(EMPTY_TEXT, String);
            expect(result).toBeDefined();
            expect(result).toEqual(true);
            done();
        });

        it('should be able to correctly identify an integer.', function (done) {
            var result = validations.isA(SAMPLE_NUMBER, Number);
            expect(result).toBeDefined();
            expect(result).toEqual(true);
            done();
        });

        it('should be able to correctly identify a floating point number.', function (done) {
            var result = validations.isA(FLOATING_NUMBER, Number);
            expect(result).toBeDefined();
            expect(result).toEqual(true);
            done();
        });

        it('should be able to correctly identify functions.', function (done) {
            var result = validations.isA(SAMPLE_FUNCTION, Function);
            expect(result).toBeDefined();
            expect(result).toEqual(true);
            done();
        });

        it('should be able to correctly identify objects.', function (done) {
            var result = validations.isA(SAMPLE_OBJECT, Object);
            expect(result).toBeDefined();
            expect(result).toEqual(true);
            done();
        });

        it('should be able to correctly identify null strings.', function (done) {
            var result = validations.isA(NULL, String);
            expect(result).toBeDefined();
            expect(result).toEqual(false);
            done();
        });

        it('should be able to correctly identify null numbers.', function (done) {
            var result = validations.isA(NULL, Number);
            expect(result).toBeDefined();
            expect(result).toEqual(false);
            done();
        });

        it('should be able to correctly identify null functions.', function (done) {
            var result = validations.isA(NULL, Function);
            expect(result).toBeDefined();
            expect(result).toEqual(false);
            done();
        });

        it('should be able to correctly identify null objects.', function (done) {
            var result = validations.isA(NULL, Object);
            expect(result).toBeDefined();
            expect(result).toEqual(false);
            done();
        });

        it('should be able to correctly identify undefined strings.', function (done) {
            var result = validations.isA(UNDEFINED, String);
            expect(result).toBeDefined();
            expect(result).toEqual(false);
            done();
        });

        it('should be able to correctly identify undefined numbers.', function (done) {
            var result = validations.isA(UNDEFINED, Number);
            expect(result).toBeDefined();
            expect(result).toEqual(false);
            done();
        });

        it('should be able to correctly identify undefined functions.', function (done) {
            var result = validations.isA(UNDEFINED, Function);
            expect(result).toBeDefined();
            expect(result).toEqual(false);
            done();
        });

        it('should be able to correctly identify undefined objects.', function (done) {
            var result = validations.isA(UNDEFINED, Object);
            expect(result).toBeDefined();
            expect(result).toEqual(false);
            done();
        });
    });

    describe('isNull function.', function () {

        it('should be able to correctly identify a null value.', function (done) {
            var result = validations.isNull(NULL);
            expect(result).toBeDefined();
            expect(result).toEqual(true);
            done();
        });

        it('should be able to correctly identify an undefined value.', function (done) {
            var result = validations.isNull(UNDEFINED);
            expect(result).toBeDefined();
            expect(result).toEqual(false);
            done();
        });

        it('should be able to correctly identify a string value.', function (done) {
            var result = validations.isNull(SAMPLE_TEXT);
            expect(result).toBeDefined();
            expect(result).toEqual(false);
            done();
        });

        it('should be able to correctly identify an empty string value.', function (done) {
            var result = validations.isNull(EMPTY_TEXT);
            expect(result).toBeDefined();
            expect(result).toEqual(false);
            done();
        });

        it('should be able to correctly identify an integer value.', function (done) {
            var result = validations.isNull(SAMPLE_NUMBER);
            expect(result).toBeDefined();
            expect(result).toEqual(false);
            done();
        });

        it('should be able to correctly identify a float value.', function (done) {
            var result = validations.isNull(FLOATING_NUMBER);
            expect(result).toBeDefined();
            expect(result).toEqual(false);
            done();
        });

        it('should be able to correctly identify an function.', function (done) {
            var result = validations.isNull(SAMPLE_FUNCTION);
            expect(result).toBeDefined();
            expect(result).toEqual(false);
            done();
        });

    });

    describe('isUndefined function.', function () {

        it('should be able to correctly identify an undefined value.', function (done) {
            var result = validations.isUndefined(UNDEFINED);
            expect(result).toBeDefined();
            expect(result).toEqual(true);
            done();
        });

        it('should be able to correctly identify a null value.', function (done) {
            var result = validations.isUndefined(NULL);
            expect(result).toBeDefined();
            expect(result).toEqual(false);
            done();
        });


        it('should be able to correctly identify a string value.', function (done) {
            var result = validations.isUndefined(SAMPLE_TEXT);
            expect(result).toBeDefined();
            expect(result).toEqual(false);
            done();
        });

        it('should be able to correctly identify an empty string value.', function (done) {
            var result = validations.isUndefined(EMPTY_TEXT);
            expect(result).toBeDefined();
            expect(result).toEqual(false);
            done();
        });

        it('should be able to correctly identify an integer value.', function (done) {
            var result = validations.isUndefined(SAMPLE_NUMBER);
            expect(result).toBeDefined();
            expect(result).toEqual(false);
            done();
        });

        it('should be able to correctly identify a float value.', function (done) {
            var result = validations.isUndefined(FLOATING_NUMBER);
            expect(result).toBeDefined();
            expect(result).toEqual(false);
            done();
        });

        it('should be able to correctly identify an function.', function (done) {
            var result = validations.isUndefined(SAMPLE_FUNCTION);
            expect(result).toBeDefined();
            expect(result).toEqual(false);
            done();
        });

    });

    describe('isNullOrUndefined function.', function () {

        it('should be able to correctly identify an undefined value.', function (done) {
            var result = validations.isNullOrUndefined(UNDEFINED);
            expect(result).toBeDefined();
            expect(result).toEqual(true);
            done();
        });

        it('should be able to correctly identify a null value.', function (done) {
            var result = validations.isNullOrUndefined(NULL);
            expect(result).toBeDefined();
            expect(result).toEqual(true);
            done();
        });


        it('should be able to correctly identify a string value.', function (done) {
            var result = validations.isNullOrUndefined(SAMPLE_TEXT);
            expect(result).toBeDefined();
            expect(result).toEqual(false);
            done();
        });

        it('should be able to correctly identify an empty string value.', function (done) {
            var result = validations.isNullOrUndefined(EMPTY_TEXT);
            expect(result).toBeDefined();
            expect(result).toEqual(false);
            done();
        });

        it('should be able to correctly identify an integer value.', function (done) {
            var result = validations.isNullOrUndefined(SAMPLE_NUMBER);
            expect(result).toBeDefined();
            expect(result).toEqual(false);
            done();
        });

        it('should be able to correctly identify a float value.', function (done) {
            var result = validations.isNullOrUndefined(FLOATING_NUMBER);
            expect(result).toBeDefined();
            expect(result).toEqual(false);
            done();
        });

        it('should be able to correctly identify an function.', function (done) {
            var result = validations.isNullOrUndefined(SAMPLE_FUNCTION);
            expect(result).toBeDefined();
            expect(result).toEqual(false);
            done();
        });

    });

    describe('exists function.', function () {

        it('should be able to correctly identify an undefined value.', function (done) {
            var result = validations.exists(UNDEFINED);
            expect(result).toBeDefined();
            expect(result).toEqual(false);
            done();
        });

        it('should be able to correctly identify a null value.', function (done) {
            var result = validations.exists(NULL);
            expect(result).toBeDefined();
            expect(result).toEqual(false);
            done();
        });


        it('should be able to correctly identify a string value.', function (done) {
            var result = validations.exists(SAMPLE_TEXT);
            expect(result).toBeDefined();
            expect(result).toEqual(true);
            done();
        });

        it('should be able to correctly identify an empty string value.', function (done) {
            var result = validations.exists(EMPTY_TEXT);
            expect(result).toBeDefined();
            expect(result).toEqual(true);
            done();
        });

        it('should be able to correctly identify an integer value.', function (done) {
            var result = validations.exists(SAMPLE_NUMBER);
            expect(result).toBeDefined();
            expect(result).toEqual(true);
            done();
        });

        it('should be able to correctly identify a float value.', function (done) {
            var result = validations.exists(FLOATING_NUMBER);
            expect(result).toBeDefined();
            expect(result).toEqual(true);
            done();
        });

        it('should be able to correctly identify an function.', function (done) {
            var result = validations.exists(SAMPLE_FUNCTION);
            expect(result).toBeDefined();
            expect(result).toEqual(true);
            done();
        });

    });

    describe('The isA function', function () {

        it('should be able to correctly identify a string.', function (done) {
            var result = validations.existsAndIsA(SAMPLE_TEXT, String);
            expect(result).toBeDefined();
            expect(result).toEqual(true);
            done();
        });

        it('should be able to correctly identify an empty string.', function (done) {
            var result = validations.existsAndIsA(EMPTY_TEXT, String);
            expect(result).toBeDefined();
            expect(result).toEqual(true);
            done();
        });

        it('should be able to correctly identify an integer.', function (done) {
            var result = validations.existsAndIsA(SAMPLE_NUMBER, Number);
            expect(result).toBeDefined();
            expect(result).toEqual(true);
            done();
        });

        it('should be able to correctly identify a floating point number.', function (done) {
            var result = validations.existsAndIsA(FLOATING_NUMBER, Number);
            expect(result).toBeDefined();
            expect(result).toEqual(true);
            done();
        });

        it('should be able to correctly identify functions.', function (done) {
            var result = validations.existsAndIsA(SAMPLE_FUNCTION, Function);
            expect(result).toBeDefined();
            expect(result).toEqual(true);
            done();
        });

        it('should be able to correctly identify objects.', function (done) {
            var result = validations.existsAndIsA(SAMPLE_OBJECT, Object);
            expect(result).toBeDefined();
            expect(result).toEqual(true);
            done();
        });

        it('should be able to correctly identify null strings.', function (done) {
            var result = validations.existsAndIsA(NULL, String);
            expect(result).toBeDefined();
            expect(result).toEqual(false);
            done();
        });

        it('should be able to correctly identify null numbers.', function (done) {
            var result = validations.existsAndIsA(NULL, Number);
            expect(result).toBeDefined();
            expect(result).toEqual(false);
            done();
        });

        it('should be able to correctly identify null functions.', function (done) {
            var result = validations.existsAndIsA(NULL, Function);
            expect(result).toBeDefined();
            expect(result).toEqual(false);
            done();
        });

        it('should be able to correctly identify null objects.', function (done) {
            var result = validations.existsAndIsA(NULL, Object);
            expect(result).toBeDefined();
            expect(result).toEqual(false);
            done();
        });

        it('should be able to correctly identify undefined strings.', function (done) {
            var result = validations.existsAndIsA(UNDEFINED, String);
            expect(result).toBeDefined();
            expect(result).toEqual(false);
            done();
        });

        it('should be able to correctly identify undefined numbers.', function (done) {
            var result = validations.existsAndIsA(UNDEFINED, Number);
            expect(result).toBeDefined();
            expect(result).toEqual(false);
            done();
        });

        it('should be able to correctly identify undefined functions.', function (done) {
            var result = validations.existsAndIsA(UNDEFINED, Function);
            expect(result).toBeDefined();
            expect(result).toEqual(false);
            done();
        });

        it('should be able to correctly identify undefined objects.', function (done) {
            var result = validations.existsAndIsA(UNDEFINED, Object);
            expect(result).toBeDefined();
            expect(result).toEqual(false);
            done();
        });
    });

    describe('existsOr function.', function () {

        it('should be able to correctly identify an undefined value.', function (done) {
            var result = validations.existsOr(UNDEFINED, SAMPLE_TEXT);
            expect(result).toBeDefined();
            expect(result).toEqual(SAMPLE_TEXT);
            done();
        });

        it('should be able to correctly identify a null value.', function (done) {
            var result = validations.existsOr(NULL, SAMPLE_TEXT);
            expect(result).toBeDefined();
            expect(result).toEqual(SAMPLE_TEXT);
            done();
        });


        it('should be able to correctly identify a string value.', function (done) {
            var result = validations.existsOr(SAMPLE_TEXT);
            expect(result).toBeDefined();
            expect(result).toEqual(SAMPLE_TEXT);
            done();
        });

        it('should be able to correctly identify an empty string value.', function (done) {
            var result = validations.existsOr(EMPTY_TEXT);
            expect(result).toBeDefined();
            expect(result).toEqual(EMPTY_TEXT);
            done();
        });

        it('should be able to correctly identify an integer value.', function (done) {
            var result = validations.existsOr(SAMPLE_NUMBER);
            expect(result).toBeDefined();
            expect(result).toEqual(SAMPLE_NUMBER);
            done();
        });

        it('should be able to correctly identify a float value.', function (done) {
            var result = validations.existsOr(FLOATING_NUMBER);
            expect(result).toBeDefined();
            expect(result).toEqual(FLOATING_NUMBER);
            done();
        });

        it('should be able to correctly identify an function.', function (done) {
            var result = validations.existsOr(SAMPLE_FUNCTION);
            expect(result).toBeDefined();
            expect(result).toEqual(SAMPLE_FUNCTION);
            done();
        });

    });

    describe('existsAndIsAOr function.', function () {

        it('should be able to correctly identify an undefined value when testing for a string.', function (done) {
            var result = validations.existsAndIsAOr(UNDEFINED, String, SAMPLE_TEXT);
            expect(result).toBeDefined();
            expect(result).toEqual(SAMPLE_TEXT);
            done();
        });

        it('should be able to correctly identify a null value when testing for a string.', function (done) {
            var result = validations.existsAndIsAOr(NULL, String, SAMPLE_TEXT);
            expect(result).toBeDefined();
            expect(result).toEqual(SAMPLE_TEXT);
            done();
        });

        it('should be able to correctly identify an undefined value when testing for a number.', function (done) {
            var result = validations.existsAndIsAOr(UNDEFINED, Number, SAMPLE_TEXT);
            expect(result).toBeDefined();
            expect(result).toEqual(SAMPLE_TEXT);
            done();
        });

        it('should be able to correctly identify a null value when testing for a number.', function (done) {
            var result = validations.existsAndIsAOr(NULL, Number, SAMPLE_TEXT);
            expect(result).toBeDefined();
            expect(result).toEqual(SAMPLE_TEXT);
            done();
        });

        it('should be able to correctly identify an undefined value when testing for an object.', function (done) {
            var result = validations.existsAndIsAOr(UNDEFINED, Object, SAMPLE_TEXT);
            expect(result).toBeDefined();
            expect(result).toEqual(SAMPLE_TEXT);
            done();
        });

        it('should be able to correctly identify a null value when testing for an object.', function (done) {
            var result = validations.existsAndIsAOr(NULL, Object, SAMPLE_TEXT);
            expect(result).toBeDefined();
            expect(result).toEqual(SAMPLE_TEXT);
            done();
        });

        it('should be able to correctly identify an undefined value when testing for a function.', function (done) {
            var result = validations.existsAndIsAOr(UNDEFINED, Function, SAMPLE_TEXT);
            expect(result).toBeDefined();
            expect(result).toEqual(SAMPLE_TEXT);
            done();
        });

        it('should be able to correctly identify a null value when testing for a function.', function (done) {
            var result = validations.existsAndIsAOr(NULL, Function, SAMPLE_TEXT);
            expect(result).toBeDefined();
            expect(result).toEqual(SAMPLE_TEXT);
            done();
        });


        it('should be able to correctly identify a string value.', function (done) {
            var result = validations.existsAndIsAOr(SAMPLE_TEXT, String, NULL);
            expect(result).toBeDefined();
            expect(result).toEqual(SAMPLE_TEXT);
            done();
        });

        it('should be able to correctly identify an empty string value.', function (done) {
            var result = validations.existsAndIsAOr(EMPTY_TEXT, String, NULL);
            expect(result).toBeDefined();
            expect(result).toEqual(EMPTY_TEXT);
            done();
        });

        it('should be able to correctly identify an integer value.', function (done) {
            var result = validations.existsAndIsAOr(SAMPLE_NUMBER, Number, NULL);
            expect(result).toBeDefined();
            expect(result).toEqual(SAMPLE_NUMBER);
            done();
        });

        it('should be able to correctly identify a float value.', function (done) {
            var result = validations.existsAndIsAOr(FLOATING_NUMBER, Number, NULL);
            expect(result).toBeDefined();
            expect(result).toEqual(FLOATING_NUMBER);
            done();
        });

        it('should be able to correctly identify an function.', function (done) {
            var result = validations.existsAndIsAOr(SAMPLE_FUNCTION, Function, NULL);
            expect(result).toBeDefined();
            expect(result).toEqual(SAMPLE_FUNCTION);
            done();
        });

        it('should be able to correctly identify an object.', function (done) {
            var result = validations.existsAndIsAOr(SAMPLE_OBJECT, Object, NULL);
            expect(result).toBeDefined();
            expect(result).toEqual(SAMPLE_OBJECT);
            done();
        });

    });

    describe('hasA function', function () {

        it('should be able to detect a property that exists.', function (done) {
            var result = validations.hasA(SAMPLE_OBJECT, 'string');
            expect(result).toBeDefined();
            expect(result).toEqual(true);
            done();
        });

        it('should correctly report the absence of a property that does not exist', function (done) {
            var result = validations.hasA(SAMPLE_OBJECT, 'blah');
            expect(result).toBeDefined();
            expect(result).toEqual(false);
            done();
        });

        it('should correctly evaluate a matcher for the given property of type string, if said property exists.', function (done) {
            var result = validations.hasA(SAMPLE_OBJECT, 'string', false, function (value) {
                return validations.existsAndIsA(value, String);
            });
            expect(result).toBeDefined();
            expect(result).toEqual(true);
            done();
        });

        it('should correctly evaluate a matcher for the given property, if said property exists.', function (done) {
            var result = validations.hasA(SAMPLE_OBJECT, 'empty', false, function (value) {
                return validations.existsAndIsA(value, String);
            });
            expect(result).toBeDefined();
            expect(result).toEqual(true);
            done();
        });

        it('should correctly evaluate a matcher for the given property of type number ( integer ) , if said property exists.', function (done) {
            var result = validations.hasA(SAMPLE_OBJECT, 'number', false, function (value) {
                return validations.existsAndIsA(value, Number);
            });
            expect(result).toBeDefined();
            expect(result).toEqual(true);
            done();
        });

        it('should correctly evaluate a matcher for the given property pf type Number ( floating point ), if said property exists.', function (done) {
            var result = validations.hasA(SAMPLE_OBJECT, 'floating', false, function (value) {
                return validations.existsAndIsA(value, Number);
            });
            expect(result).toBeDefined();
            expect(result).toEqual(true);
            done();
        });

        it('should correctly evaluate a matcher for the given property of type function, if said property exists.', function (done) {
            var result = validations.hasA(SAMPLE_OBJECT, 'fun', false, function (value) {
                return validations.existsAndIsA(value, Function);
            });
            expect(result).toBeDefined();
            expect(result).toEqual(true);
            done();
        });

        it('should correctly evaluate a matcher for the given property of type null, if said property exists.', function (done) {
            var result = validations.hasA(SAMPLE_OBJECT, 'none', false, function (value) {
                return validations.isNull(value);
            });
            expect(result).toBeDefined();
            expect(result).toEqual(true);
            done();
        });

        it('should correctly evaluate a matcher for the given property of type undefined, if said property exists.', function (done) {
            var result = validations.hasA(SAMPLE_OBJECT, 'undef', false, function (value) {
                return validations.isUndefined(value, undefined);
            });
            expect(result).toBeDefined();
            expect(result).toEqual(true);
            done();
        });
    });
});