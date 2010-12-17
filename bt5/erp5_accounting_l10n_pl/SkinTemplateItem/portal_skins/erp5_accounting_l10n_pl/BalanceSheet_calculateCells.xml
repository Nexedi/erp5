<?xml version="1.0"?>
<ZopeData>
  <record id="1" aka="AAAAAAAAAAE=">
    <pickle>
      <global name="PythonScript" module="Products.PythonScripts.PythonScript"/>
    </pickle>
    <pickle>
      <dictionary>
        <item>
            <key> <string>Script_magic</string> </key>
            <value> <int>3</int> </value>
        </item>
        <item>
            <key> <string>_bind_names</string> </key>
            <value>
              <object>
                <klass>
                  <global name="NameAssignments" module="Shared.DC.Scripts.Bindings"/>
                </klass>
                <tuple/>
                <state>
                  <dictionary>
                    <item>
                        <key> <string>_asgns</string> </key>
                        <value>
                          <dictionary>
                            <item>
                                <key> <string>name_container</string> </key>
                                <value> <string>container</string> </value>
                            </item>
                            <item>
                                <key> <string>name_context</string> </key>
                                <value> <string>context</string> </value>
                            </item>
                            <item>
                                <key> <string>name_m_self</string> </key>
                                <value> <string>script</string> </value>
                            </item>
                            <item>
                                <key> <string>name_subpath</string> </key>
                                <value> <string>traverse_subpath</string> </value>
                            </item>
                          </dictionary>
                        </value>
                    </item>
                  </dictionary>
                </state>
              </object>
            </value>
        </item>
        <item>
            <key> <string>_body</string> </key>
            <value> <string>getInventory=context.FiscalReportCell_doGetInventory\n
\n
# pobiera stan kont po stronie credit\n
getCredit=context.getCredit\n
\n
# pobiera stan kont po stronie debit\n
getDebit=context.getDebit\n
\n
# pobiera różnicę dla kont po obu stronach \n
getBalance=context.getBalance\n
\n
class Bil:pass\n
bil=Bil()\n
\n
bil.AI1=getBalance((\'022\',))+getBalance((\'072\',))\n
bil.AI2=getBalance((\'023\',))+getBalance((\'073\',))\n
bil.AI3=getBalance((\'025\',))+getBalance((\'074\',))\n
bil.AI4=getBalance((\'206\',\'216\'))\n
bil.AI=bil.AI1+bil.AI2+bil.AI3+bil.AI4\n
\n
bil.AII1a=getBalance((\'011\',\'016\'))+getBalance((\'066\',))\n
bil.AII1b=getBalance((\'012\',))+getBalance((\'062\',))\n
bil.AII1c=getBalance((\'013\',))+getBalance((\'063\',))\n
bil.AII1d=getBalance((\'014\',))+getBalance((\'064\',))\n
bil.AII1e=getBalance((\'015\',\'017\'))+getBalance((\'065\',\'067\'))\n
bil.AII1=bil.AII1a+bil.AII1b+bil.AII1c+bil.AII1d+bil.AII1e\n
bil.AII2=getBalance((\'081\',\'082\',\'083\'))+getBalance((\'086\',))\n
bil.AII3=getBalance((\'206\',\'216\'))\n
bil.AII=bil.AII1+bil.AII2+bil.AII3\n
\n
bil.AIII=getBalance((\'248\',)) # XXX:280\n
\n
bil.AIV1=getBalance((\'031\',))-getBalance((\'041\',))\n
bil.AIV2=getBalance((\'032\',))-getBalance((\'042\',))\n
bil.AIV3a1=getBalance((\'033\',))-getBalance((\'043\',))\n
bil.AIV3a2=getBalance((\'034\',))-getBalance((\'044\',))\n
bil.AIV3a3=getBalance((\'252\',))-getBalance((\'280\',))\n
bil.AIV3a4=getBalance((\'035\',))-getBalance((\'045\',))\n
bil.AIV3a=bil.AIV3a1+bil.AIV3a2+bil.AIV3a3\n
bil.AIV3b1=getBalance((\'036\',))-getBalance((\'46\',))\n
bil.AIV3b2=getBalance((\'037\',))-getBalance((\'47\',))\n
bil.AIV3b3=getBalance((\'254\',)) # XXX:280\n
bil.AIV3b4=getBalance((\'038\',))-getBalance((\'48\',))\n
bil.AIV3b=bil.AIV3b1+bil.AIV3b2+bil.AIV3b3\n
bil.AIV3=bil.AIV3a+bil.AIV3b\n
bil.AIV4=getBalance((\'039\',))-getBalance((\'49\',))\n
bil.AIV=bil.AIV1+bil.AIV2+bil.AIV3+bil.AIV4\n
\n
bil.AV1=getBalance((\'643\',))\n
bil.AV2=getBalance((\'641\',\'642\'))\n
bil.AV=bil.AV1+bil.AV2\n
\n
bil.A=bil.AI+bil.AII+bil.AIII+bil.AIV+bil.AV\n
\n
bil.BI1=getBalance((\'31\',\'301\'))+getBalance((\'341\',))\n
bil.BI2=getBalance((\'602\',\'630\',\'501\',\'502\',\'504\',\'531\'))-getBalance((\'622\',))\n
bil.BI3=getBalance((\'607\',\'670\'))-getBalance((\'622\',))\n
bil.BI4=getBalance((\'331\',\'332\',\'333\',\'338\',\'339\',\'303\'))-getBalance((\'342\',\'343\',\'344\',\'345\'))\n
bil.BI5=getBalance((\'206\',\'216\'))\n
bil.BI=bil.BI1+bil.BI2+bil.BI3+bil.BI4+bil.BI5\n
\n
bil.BII1a=getBalance((\'211\',\'213\',\'247\'))\n
bil.BII1b=getBalance((\'248\',))\n
bil.BII1=bil.BII1a+bil.BII1b\n
bil.BII2a=getBalance((\'201\',\'203\',\'247\'))\n
bil.BII2b=max(getBalance((\'22\',)),0) # rozrachunki?\n
bil.BII2c=max(getBalance((\'231\',\'234\',\'243\',\'245\',\'248\',\'251\',\'257\',\'258\')),0)\n
bil.BII2d=getBalance((\'244\',))\n
bil.BII2=bil.BII2a+bil.BII2b+bil.BII2c+bil.BII2d\n
bil.BII=bil.BII1+bil.BII2\n
\n
bil.BIII1a=getBalance((\'141\',\'142\',\'143\',\'252\'))-getBalance((\'144\',)) # XXX: skomasowane\n
bil.BIII1b=getBalance((\'146\',\'147\',\'148\',\'254\'))-getBalance((\'149\',)) # XXX: skomasowane\n
bil.BIII1c1=getBalance((\'10\',\'13\'))-getBalance((\'138\',))\n
bil.BIII1c2=getBalance((\'159\',))\n
bil.BIII1c3=getBalance((\'156\',))\n
bil.BIII1c=bil.BIII1c1+bil.BIII1c2+bil.BIII1c3\n
bil.BIII1=bil.BIII1a+bil.BIII1b+bil.BIII1c\n
bil.BIII2=getBalance((\'160\',))-getBalance((\'165\',))\n
bil.BIII=bil.BIII1+bil.BIII2\n
\n
bil.BIV=getBalance((\'641\',\'642\'))\n
\n
bil.B=bil.BI+bil.BII+bil.BIII+bil.BIV\n
\n
bil.aktywa=bil.A+bil.B\n
\n
bil.pAI=-getBalance((\'801\',))\n
bil.pAII=-getBalance((\'251\',))\n
bil.pAIII=-getBalance((\'150\',))\n
bil.pAIV=-getBalance((\'806\',))\n
bil.pAV=-getBalance((\'807\',))\n
bil.pAVI=-getBalance((\'808\',))\n
bil.pAVII=-getBalance((\'821\',))\n
pl=context.ProfitAndLoss_calculateCells()\n
bil.pAVIII=pl.N\n
#bil.pAVIII=-942 # call ProfitAndLoss_calculateCells\n
bil.pAIX=-getBalance((\'822\',))\n
bil.pA=bil.pAI+bil.pAII+bil.pAIII+bil.pAIV+bil.pAV+bil.pAVI+bil.pAVII+bil.pAVIII+bil.pAIX\n
\n
bil.pBI1=-getBalance((\'831\',))\n
bil.pBI2=-getBalance((\'833\',)) # zmienione\n
bil.pBI3=-getBalance((\'832\',\'834\',\'646\'))\n
bil.pBI=bil.pBI1+bil.pBI2+bil.pBI3\n
bil.pBII1=0 # zmienione - nie mamy tego rozr�nienia\n
bil.pBII2a=-getBalance((\'138\',\'255\'))\n
bil.pBII2b=-getBalance((\'259\',))\n
bil.pBII2c=-getBalance((\'251\',\'256\',\'258\'))\n
bil.pBII2d=0\n
bil.pBII2=bil.pBII2a+bil.pBII2b+bil.pBII2c+bil.pBII2d\n
bil.pBII=bil.pBII1+bil.pBII2\n
bil.pBIII1=0 # jw\n
bil.pBIII2a=-getBalance((\'139\',\'255\'))\n
bil.pBIII2b=-getBalance((\'259\',))\n
bil.pBIII2c=-getBalance((\'251\',\'256\',\'257\',\'258\'))\n
bil.pBIII2d=-getBalance((\'202\',\'204\',\'246\',\'301\',\'302\',\'303\',\'304\'))\n
bil.pBIII2e=-getBalance((\'205\',\'842\'))\n
bil.pBIII2f=-getBalance((\'207\',))\n
bil.pBIII2g=-min(getBalance((\'22\',)),0) # rozrachunki?\n
bil.pBIII2h=-min(getBalance((\'231\',)),0)\n
bil.pBIII2i=-min(getBalance((\'234\',\'245\',\'248\',\'257\')),0)\n
bil.pBIII2=bil.pBIII2a +bil.pBIII2b +bil.pBIII2c +bil.pBIII2d +bil.pBIII2e +bil.pBIII2f +bil.pBIII2g +bil.pBIII2h +bil.pBIII2i\n
bil.pBIII3=-getBalance((\'851\',\'859\'))\n
bil.pBIII=bil.pBIII1+bil.pBIII2+bil.pBIII3\n
bil.pBIV1=-getBalance((\'841\',))\n
bil.pBIV2=-getBalance((\'843\',\'844\',\'845\')) # czy rozr�nienie termin�w jest wa�ne? to tzreba by albo zmieni� plan kont, albo liczy� wg terminu\n
bil.pBIV=bil.pBIV1+bil.pBIV2\n
\n
bil.pB=bil.pBI+bil.pBII+bil.pBIII\n
\n
bil.pasywa=bil.pA+bil.pB\n
\n
\n
\n
\n
\n
\n
\n
\n
\n
\n
\n
\n
\n
return bil\n
\n
# vim:syntax=python\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>BalanceSheet_calculateCells</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
