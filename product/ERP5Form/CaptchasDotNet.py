# -*- coding: utf-8 -*-
#---------------------------------------------------------------------       
# Python module for easy utilization of http://captchas.net
#
# For documentation look at http://captchas.net/sample/python/
# 
# Written by Sebastian Wilhelmi <seppi@seppi.de> and
#            Felix Holderied <felix@holderied.de>
# This file is in the public domain.
#
# ChangeLog:
#
# 2010-01-15: Adapt to ERP5 : a lot of code had to be removed or changed.
#            Most of the work must be done in another class.
#
# 2006-09-08: Add new optional parameters alphabet, letters 
#             height an width. Add audio_url. 
#      
# 2006-03-01: Only delete the random string from the repository in
#             case of a successful verification.
#
# 2006-02-14: Add new image() method returning an HTML/JavaScript
#             snippet providing a fault tolerant service.
#
# 2005-06-02: Initial version.
#
#---------------------------------------------------------------------

import md5
import random

class CaptchasDotNet:
    def __init__ (self, client, secret,
                  alphabet = 'abcdefghkmnopqrstuvwxyz',
                  letters = 6,
                  width = 240,
                  height = 80
                  ):
        self.__client = client
        self.__secret = secret
        self.__alphabet = alphabet
        self.__letters = letters
        self.__width = width
        self.__height = height

    # Return a random string
    def random_string (self):
        # The random string shall consist of small letters, big letters
        # and digits.
        letters = "abcdefghijklmnopqrstuvwxyz"
        letters += letters.upper () + "0123456789"

        # The random starts out empty, then 40 random possible characters
        # are appended.
        random_string = ''
        for i in range (40):
            random_string += random.choice (letters)

        # Return the random string.
        return random_string

    def image_url (self, random, base = 'http://image.captchas.net/'):
        url = base
        url += '?client=%s&amp;random=%s' % (self.__client, random)
        if self.__alphabet != "abcdefghijklmnopqrstuvwxyz":
            url += '&amp;alphabet=%s' % self.__alphabet
        if self.__letters != 6:
            url += '&amp;letters=%s' % self.__letters
        if self.__width != 240:
            url += '&amp;width=%s' % self.__width
        if self.__height != 80:
            url += '&amp;height=%s' % self.__height
        return url

    def audio_url (self, random, base = 'http://audio.captchas.net/'):
        url = base
        url += '?client=%s&amp;random=%s' % (self.__client, random)
        if self.__alphabet != "abcdefghijklmnopqrstuvwxyz":
            url += '&amp;alphabet=%s' % self.__alphabet
        if self.__letters != 6:
            url += '&amp;letters=%s' % self.__letters
        return url

    def image (self, random, id = 'captchas.net'):
        return '''
        <a href="http://captchas.net"><img
            style="border: none; vertical-align: bottom"
            id="%s" src="%s" width="%d" height="%d"
            alt="The CAPTCHA image" /></a>
        <script type="text/javascript">
          <!--
          function captchas_image_error (image) 
          {
            if (!image.timeout) return true;
            image.src = image.src.replace (/^http:\/\/image\.captchas\.net/, 
                                           'http://image.backup.captchas.net');
            return captchas_image_loaded (image);
          }

          function captchas_image_loaded (image)
          {
            if (!image.timeout) return true;
            window.clearTimeout (image.timeout);
            image.timeout = false;
            return true;
          }

          var image = document.getElementById ('%s');
          image.onerror = function() {return captchas_image_error (image);};
          image.onload = function() {return captchas_image_loaded (image);};
          image.timeout 
            = window.setTimeout(
               "captchas_image_error (document.getElementById ('%s'))",
               10000);
          image.src = image.src;
          //-->      
        </script>''' % (id, self.image_url (random), self.__width, self.__height, id, id)
        
    def get_answer (self, random ):
        # The format of the password.
        password_alphabet = self.__alphabet
        password_length = self.__letters

        # Calculate the MD5 digest of the concatenation of secret key and
        # random string.
        encryption_base = self.__secret + random
        if (password_alphabet != "abcdefghijklmnopqrstuvwxyz") or (password_length != 6):
            encryption_base += ":" + password_alphabet + ":" + str(password_length)
        digest = md5.new (encryption_base).digest ()

        # Compute password
        correct_password = ''
        for pos in range (password_length):
            letter_num = ord (digest[pos]) % len (password_alphabet)
            correct_password += password_alphabet[letter_num]
        
        return correct_password
