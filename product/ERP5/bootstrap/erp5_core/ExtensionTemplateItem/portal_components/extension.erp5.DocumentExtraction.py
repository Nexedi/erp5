##############################################################################
#
# Copyright (c) 2006-2007 Nexedi SA and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import string, re

redundant_chars='"\'.:;,-+<>()*~' # chars we need to strip from a word before we see if it matches, and from the searchwords to eliminate boolean mode chars
tr=string.maketrans(redundant_chars,' '*len(redundant_chars))

class Done(Exception):
  pass

class Word(str):pass

class FoundWord(str):

  def __str__(self):
    return self.tags[0]+self+self.tags[1]

class Part:

  def __init__(self, tags, trail): #  pylint: disable=redefined-outer-name
    self.chain=[]
    self.limit=trail
    self.trail=trail
    self.has=False
    self.tags=tags

  def push(self,w):
    self.chain.insert(0,Word(w))
    if len(self.chain)>self.limit:
      if self.has:
        self.chain.reverse()
        raise Done()
      self.chain.pop()

  def add(self,w):
    self.chain.insert(0,FoundWord(w))
    self.limit+=self.trail+1
    self.has=True

  def __str__(self):
    return '...%s...' % ' '.join(map(str,self.chain))



def generateParts(_, text, sw, tags, trail, maxlines): #  pylint: disable=redefined-outer-name
  par=Part(tags,trail)
  sw=sw.translate(tr).strip().lower().split()
  test=lambda w:w.translate(tr).strip().lower() in sw
  i=0
  length=len(text)
  for counter,aw in enumerate(text):
    if i==maxlines:
      raise StopIteration
    if test(aw):
      par.add(aw)
    else:
      try:
        par.push(aw)
      except Done:
        i+=1
        yield par
        par=Part(tags,trail)
      if counter==length-1:
        if par.has:
          par.chain.reverse()
          yield par # return the last marked part


def getExcerptText(context, txt, sw, tags, trail, maxlines): #  pylint: disable=redefined-outer-name
  """
  Returns an excerpt of text found in the txt string
  """
  txt = str(txt)
  # initialize class
  FoundWord.tags=tags
  # strip html tags (in case it is a web page - we show result without formatting)
  r = re.compile('<script>.*?</script>',re.DOTALL|re.IGNORECASE)
  r = re.compile('<head>.*?</head>',re.DOTALL|re.IGNORECASE)
  txt = re.sub(r,'',txt)
  r = re.compile('<([^>]+)>',re.DOTALL|re.IGNORECASE)
  txt = re.sub(r,'',txt)
  txt = txt.replace('-',' - ') # to find hyphenated occurrences
  txt = txt.replace(',',', ')
  txt = txt.replace(';','; ')
  r = re.compile(r'\s+')
  txt = re.sub(r,' ',txt)
  text = ' '.join(txt.split('\n')).split(' ') # very rough tokenization
  return [x for x in generateParts(context, text, sw, tags, trail, maxlines)]


if __name__=='__main__':
  sw='pricing priority right acting proportion'
  txt=' '.join([l.strip() for l in open('offer.txt').readlines()])

  # configuration

  tags=('<b>','</b>')
  trail=5
  maxlines=5
  for p in getExcerptText(None,txt,sw,tags,trail,maxlines):
    print p


# vim: filetype=python syntax=python shiftwidth=2
