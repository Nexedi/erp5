class Number:
    DIC  = {0:'Zéro', 1:'un',2:'deux',3:'trois',4:'quatre',5:'cinq',6:'six',7:'sept', 8:'huit',9:'neuf',
            10:'dix',11:'onze',12:'douze',13:'treize', 14:'quatorze',15:'quinze',16:'seize',17:'dix-sept',
            18:'dix-huit',19:'dix-neuf',20:'vingt',30:'trente',40:'quarante',50:'cinquante', 60:'soixante',
            80:'quatre vingt',100:'cent',1000:'mille',1000000:'million',1000000000:'milliard'}

    def MinusHumdred(self,MyNumber):
        #context.log('MinusHumdred', MyNumber)
        if MyNumber == 0:
            return ''
        elif MyNumber in self.DIC:
            return self.DIC[MyNumber]
        elif MyNumber < 60:
            return self.DIC[10*(MyNumber/10)]+self.iif(MyNumber%10==1, ' et ',' ')+self.DIC[MyNumber%10]
        elif MyNumber < 80:
            return self.DIC[60]+self.iif(MyNumber%10==1, ' et ',' ')+self.DIC[MyNumber - 60]
        elif MyNumber < 100:
            return self.DIC[80]+' '+self.DIC[MyNumber - 80]

    def iif(self, condition,trueVal,falseVal):
        if condition:
            return trueVal
        else:
            return falseVal

    def convert(self,MyNumber,step=1000000000, Hundred=False):
        if MyNumber <= 100:
            return self.MinusHumdred(MyNumber)
        elif MyNumber < step:
            return self.convert(MyNumber,step/self.iif(step>1000,1000,10),Hundred)
        elif MyNumber < 2*step:
            return self.iif(step>1000,'un ','')+self.DIC[step] + self.iif(MyNumber%step>0,' ','') + self.convert(MyNumber%step, step/self.iif(step>1000,1000,10),Hundred)
        else:
            return (self.convert(MyNumber/step, step/self.iif(step>1000,1000,10),(Hundred or step>100)) +' '+
                    self.DIC[step]+self.iif(step == 1000 or (step == 100 and (MyNumber%step > 0 or Hundred)),'','s') +
                    self.iif(MyNumber%step>0,' ','') + self.convert(MyNumber%step, step/self.iif(step>1000,1000,10),Hundred))

    def numbertoletter(self,aNumber):
        return self.iif(aNumber == 0, self.DIC[0], self.convert(aNumber))
#return pvalue
v_value = Number()

prefix = ''
if pvalue < 0:
  prefix = '-'
  pvalue = -pvalue
return prefix + v_value.numbertoletter(pvalue)
