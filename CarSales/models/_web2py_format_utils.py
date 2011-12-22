# coding: utf8
#web2py_brasil_utils
#####################################################################
#
# web2py Brasil Utils - http://www.web2pybrasil.com.br
#
# Coleção de functions e helpers que ajudam no desenvolvi-
# mento de uma aplicação web2py em idioma português brasil.
#
# How To: Inclua este arquivo em sua pasta models
# 
# SafeBRLocale() -> Efetua o acerto de localização - Thread Unsafe
# Moeda() -> Formata decimais, inteiros e flutuantes para R$
# Data() -> Formata datetima para data brasileira
#
#
# Colabore com este projeto
#
#
#####################################################################

# Define Locale
def SafeLocale():
    from locale import setlocale, LC_ALL
    try:
       setlocale(LC_ALL,'en_US.UTF-8')
    except:
       setlocale(LC_ALL,'english')    


# Formata moeda ###
def Money(price, formated=True):
    """
    >>> print Money(10000)
    $ 10.000,00
    >>> print Money(10000,False)
    10.000,00
    """
    SafeLocale()
    from locale import currency
    if formated:
        return '$ %s' % currency(price, grouping=True, symbol=False)
    else:
        return currency(price, grouping=False, symbol=False).replace(',','')
    

def Date(date,format=1):
    """    
    >>> SafeLocale()
    >>> from datetime import datetime
    >>> date = datetime.strptime('2010-08-01','%Y-%m-%d')
    >>> print Date(date)
    01/08/2010
    >>> print Date(date,2)
    Sun, 01 Aug of 2010
    >>> print Date(date,3)
    Sunday, 01 august of 2010
    """
    if formato == 2:
        format="%a, %d %b of %Y"
    elif formato == 3:
        format="%A, %d %B of %Y"
    else:
        format="%d/%m/%Y"
        
    return data.date().strftime(format)
