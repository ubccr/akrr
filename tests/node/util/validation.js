var VALIDATION = {

    isA: function (obj, type, eager) {
        var eager = eager || false;

        var aType = this._toType(obj);
        var eType = this._toType(type);
        if (eType === 'function') {
            eType = this._toType(new type());
        }
        var result = aType === eType;
        if (!result && eager) {
            throw new Error("Expected a '" + eType + "' but got a '" + aType + "'.");
        } else {
            return result;
        }
    },

    isNull: function (obj, eager) {
        var eager = eager || false;
        var result = obj === null;
        if (!result && eager) {
            throw new Error('Expected non-null value, received null.');
        } else {
            return result;
        }
    },

    isUndefined: function (obj, eager) {
        var eager = eager || false;
        var result = obj === undefined;
        if (!result && eager) {
            throw new Error('Expected a defined value, received undefined.');
        } else {
            return result;
        }
    },

    isNullOrUndefined: function (obj, eager) {
        var eager = eager || false;
        var result = obj === null || obj === undefined;
        if (!result && eager) {
            throw new Error('Expected a non null and defined value. Received a null or undefined value.');
        } else {
            return result;
        }
    },

    exists: function (obj, eager) {
        var eager = eager || false;
        var result = !this.isNullOrUndefined(obj);
        if (!result && eager) {
            throw new Error('Expected a non null and defined value. Received a null or undefined value.');
        } else {
            return result;
        }
    },

    existsAndIsA: function (obj, type, eager) {
        var eager = eager || false;
        var isNotNullOrUndefined = !this.isNullOrUndefined(obj);
        var isA = this.isA(obj, type);
        if (!isNotNullOrUndefined && eager) {
            throw new Error('Expected a value that was non null or defined.');
        } else if (!isA && eager) {
            throw new Error("Expected a value of type '" + this._toType(type) + "' but received '" + this._toType(obj) + "'");
        } else {
            return isNotNullOrUndefined && isA;
        }
    },

    existsOr: function (obj, fallback) {
        return this.exists(obj) ? obj : fallback;
    },

    existsAndIsAOr: function (obj, type, fallback) {
        return this.existsAndIsA(obj, type) ? obj : fallback;
    },

    hasA: function (obj, property, eager, matcher) {
        var isValid = this.exists(obj) && this.existsAndIsA(property, String);
        if (!isValid && eager) {
            throw new Error('Expected an object with a property of type string.');
        } else if (!isValid) {
            return false;
        }
        var result = property in obj;
        if (!result && eager) {
            throw new Error("Expected to find '" + property + "'. ");
        } else if (!result && !eager) {
            return false;
        } else {
            var matcherIsValid = this.exists(matcher) && this.isA(matcher, Function);
            return matcherIsValid ? matcher(obj[property]) : result;
        }
    },

    _toType: function (obj) {
        return ({}).toString.call(obj).match(/\s([a-z|A-Z]+)/)[1].toLowerCase();
    }
};

module.exports = VALIDATION;