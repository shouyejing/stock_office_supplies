{
    'name': "Office Supplies Management",
    'version': '1.0',
    'depends': ['base', 'stock'],
    'author': "wangting",
    'category': 'custom',
    'data': [
        'data_base.xml',
        'security/stock_office_supplies_security.xml',
        'views/borrow.xml',
        'views/borrow_workflow.xml',
        'data.xml'
    ],
    'application': True,
    'description': """
    版本1.73

    support for odoo 8
    """
}