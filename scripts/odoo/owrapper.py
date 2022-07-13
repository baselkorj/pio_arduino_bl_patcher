import odoo.oclient as client
import os
from getpass import getpass
from datetime import datetime

_url = 'odoodev.sulaimanhabsi.com'
_db = 'aphcarios'
_user = ""
_pwd = ""

_odoo = None


def setCredentials(server='odoodev.sulaimanhabsi.com', user=_user, password=_pwd):
    global _user, _pwd, _url
    _user = user
    _url = server
    _pwd = password


def signIn():
    global _odoo
    global _pwd
    _odoo = client.OdooClient(host=_url,
                              dbname=_db, protocol='xmlrpcs', port=443)

    if _odoo:
        try:
            if os.path.exists('password.txt'):
                # print('password file exists')
                f = open('password.txt', 'r')
                _pwd = f.read()
            elif _pwd != '':
                uid = _odoo.Authenticate(_user, _pwd)
            else:
                _pwd = getpass(prompt='Password: ', stream=None)
                # print(p)
                uid = _odoo.Authenticate(_user, _pwd)
            return uid
        except:
            return False

    else:
        return False


def getProductLots(productName):
    products = _odoo.SearchRead('stock.production.lot', [
                                ('product_id', '=', productName)], ['name'])
    return products


def createProductLot(name, product_id, firmware):
    newProductLot = _odoo.Create('stock.production.lot', {
        'name': name,
        'product_id': product_id,
        'company_id': 1,
        'note': 'PCB Flash Date: ' + datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + ' | Firmware Version: ' + firmware
    })
    return newProductLot
