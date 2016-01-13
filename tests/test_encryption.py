import unittest
import uuid
import hashlib


class HashTest(unittest.TestCase):

    def _hash(self, content, hash_method=hashlib.sha256, salt=uuid.uuid4().hex):
        return '%s%s' % (hash_method(salt.encode() + content.encode()).hexdigest(), salt)

    def _check(self, hashed, raw, hash_method=hashlib.sha256, hash_length=64):
        content = hashed[:hash_length]
        salt = hashed[hash_length:]
        return content == hash_method(salt.encode() + raw.encode()).hexdigest()

    def hash_512(self, content):
        return self._hash(content, hashlib.sha512)

    def check_512(self, hashed, raw):
        return self._check(hashed, raw, hashlib.sha512, 128)

    def hash(self, content):
        return self._hash(content)

    def check(self, hashed, raw):
        return self._check(hashed, raw)

    def test_hashing(self):
        un_hashed = ''
        hashed = self.hash_512(un_hashed)
        result = self.check_512(hashed, un_hashed)
        self.assertTrue(result, 'Expected check(hashed, un_hashed) => true. Received: %r' % (result, ))

    def test_username_password_512(self):
        print 'Test that the REST API user auth mechanism can be updated to utilize encryption...'
        un_hashed = (
            ('rw', 'Ohf4oZ6w'),
            ('ro', 'xei3aFai')
        )

        for unhashed_username, unhashed_password in un_hashed:
            print 'The following would be kept on the server: %s, %s' % (unhashed_username, unhashed_password)

            hashed_username = self.hash_512(unhashed_username)
            hashed_password = self.hash_512(unhashed_password)

            print 'The following would be provided to the client: %s, %s' % (hashed_username, hashed_password)

            self.assertTrue(self.check_512(hashed_username, unhashed_username), 'Expected the username(s) to check out.')
            self.assertTrue(self.check_512(hashed_password, unhashed_password), 'Expected the password(s) to check out.')

        print 'Test Complete!'
        print '*' * 80

    def test_username_password_256(self):
        print 'Test that the REST API user auth mechanism can be updated to utilize encryption...'
        un_hashed = (
            ('rw', 'Ohf4oZ6w'),
            ('ro', 'xei3aFai')
        )

        for unhashed_username, unhashed_password in un_hashed:
            print 'The following would be kept on the server: %s, %s' % (unhashed_username, unhashed_password)

            hashed_username = self.hash(unhashed_username)
            hashed_password = self.hash(unhashed_password)

            print 'The following would be provided to the client: %s, %s' % (hashed_username, hashed_password)

            self.assertTrue(self.check(hashed_username, unhashed_username), 'Expected the username(s) to check out.')
            self.assertTrue(self.check(hashed_password, unhashed_password), 'Expected the password(s) to check out.')

        print 'Test Complete!'
        print '*' * 80