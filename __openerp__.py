{
    'name': "stock_office_supplies",
    'version': '1.0',
    'depends': ['base', 'stock'],
    'author': "wangting",
    'category': 'custom',
    'data': [
        'views/borrow.xml',
        'views/borrow_workflow.xml',
        'security/stock_office_supplies_security.xml',
        'data.xml'
    ],
    'application': True,
    'description': """
    版本1.53


    support for odoo 8
    """
}