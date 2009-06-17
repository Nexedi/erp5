from Products.ERP5Type.UnrestrictedMethod import UnrestrictedMethod

def getProductPrice(product):
    getPrice = UnrestrictedMethod(product.getPrice)
    return getPrice()
