import cmmac

def CMLang(langue):
    if langue == 'fr':
        langue = 'francais'
    elif langue == 'en':
        langue = 'anglais'
    return langue

def CreerFormulaireCM(url_banque = "https://ssl.paiement.cic-banques.fr",
                        version = "1.2",
                        TPE = "/var/www/payment/storever.key",
                        montant = "1EUR",
                        reference = "STVR1",
                        texte_libre = "Toto",
                        url_retour = "http://www.storever.com",
                        url_retour_ok = "https://secure.storever.com/payment/accept",
                        url_retour_err = "https://secure.storever.com/payment/reject",
                        langue = "fr",
                        code_societe = "storever",
                        texte_bouton = "Paiement par carte bancaire"):
    # Create Bing String
    formulaire = '1234567890' * 500
    langue = CMLang(langue)
    formulaire = cmmac.CreerFormulaireCM2(url_banque, version, TPE, str(montant)+'EUR', str(reference), texte_libre, url_retour, url_retour_ok, url_retour_err, langue, str(code_societe), texte_bouton, formulaire)
    return formulaire

def CalculMAC(version="",
              TPE="",
              cdate="",
              montant="",
              reference="",
              texte_libre="",
              langue="",
              code_societe=""):
    # Adapt Parameters
    langue = CMLang(langue)
    return cmmac.CalculMAC(version,TPE,cdate,montant,reference,texte_libre,langue,code_societe)

def TestMAC(code_MAC="",
            version="",
            TPE="",
            cdate="",
            montant="",
            reference="",
            texte_libre="",
            code_retour="Code Retour Par Défaut"):
    return cmmac.TestMAC(code_MAC,version,TPE,cdate,montant,reference,texte_libre,code_retour)

def CreerReponseCM(phrase=""):
    # Create Bing String
    reponse = '1234567890' * 500
    return cmmac.CreerReponseCM2(phrase,reponse)
