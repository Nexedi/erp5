

class Done(Exception):
  pass

class Word(str):pass

class FoundWord(str):
  
  def __str__(self):
    return self.tags[0]+self+self.tags[1]

class Part:

  def __init__(self,tags,trail):
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
    #import pdb
    #pdb.set_trace()
    self.chain.insert(0,FoundWord(w))
    self.limit+=self.trail+1
    self.has=True

  def __str__(self):
    return '...%s...' % ' '.join(map(str,self.chain))

def generateParts(context,text,sw,tags,trail,maxlines):
  par=Part(tags,trail)
  test=lambda w:w.strip().replace('"','').replace("'","") in sw
  i=0
  for aw in text:
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


def cutFound(context,txt,sw,tags,trail,maxlines):
  FoundWord.tags=tags
  text = txt.split(' ') # very rough tokenization
  return [p for p in generateParts(context,text,sw,tags,trail,maxlines)]


if __name__=='__main__':
  sw='pricing priority right acting proportion'
  txt=' '.join([l.strip() for l in open('offer.txt').readlines()])

  # configuration

  tags=('<b>','</b>')
  trail=5
  maxlines=5
  sw=sw.split()
  for p in cutFound(txt,sw,tags,trail,maxlines):
    print p


# vim: filetype=python syntax=python shiftwidth=2 
