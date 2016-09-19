# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""

from mingtak.allpay import _
from zope import schema
from zope.interface import Interface
from plone.autoform import directives as form
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm


class IMingtakAllpayLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


ORDER_STATE = SimpleVocabulary(
    [SimpleTerm(value=u'ordered', title=_(u'ordered')),
     SimpleTerm(value=u'paid', title=_(u'paid')),
     SimpleTerm(value=u'shipped', title=_(u'shipped')),
     SimpleTerm(value=u'arrived', title=_(u'arrived')),
     SimpleTerm(value=u'inreturn', title=_(u'inreturn')),
     SimpleTerm(value=u'returned', title=_(u'returned')),
     SimpleTerm(value=u'overdue', title=_(u'overdue')),]
    )


class IOrder(Interface):
    """ 訂單 """
    title = schema.TextLine(
        title=_(u"Order Title"),
        description=_(u"Mapping to allPay's MerchantTradeNo"),
        required=True,
    )

    description = schema.Text(
        title=_(u"Description"),
        description=_(u"Mapping to allPay's ItemName"),
        required=False,
    )

    receiver = schema.TextLine(
        title=_(u"Receiver"),
        description=_(u"Receiver name."),
        required=False,
    )

    phone = schema.TextLine(
        title=_(u"Phone"),
        description=_(u"Phone Number."),
        required=False,
    )

    cellPhone = schema.TextLine(
        title=_(u"Cell Phone"),
        description=_(u"Cell Phone number."),
        required=False,
    )

    email = schema.TextLine(
        title=_(u"Email"),
        description=_(u"Email."),
        required=False,
    )


    addr_city = schema.TextLine(
        title=_(u"City"),
        description=_(u"City name."),
        required=False,
    )

    addr_district = schema.TextLine(
        title=_(u"District"),
        description=_(u"District"),
        required=False,
    )

    addr_zip = schema.TextLine(
        title=_(u"ZIP Code"),
        description=_(u"ZIP code"),
        required=False,
    )

    addr_address = schema.TextLine(
        title=_(u"Address"),
        description=_(u"Address"),
        required=False,
    )

    taxId = schema.TextLine(
        title=_(u"Tax ID"),
        description=_(u"Tax ID"),
        required=False,
    )

    invoiceTitle = schema.TextLine(
        title=_(u"Invoice Title"),
        description=_(u"Invoice Title"),
        required=False,
    )

    form.write_permission(productUIDs='cmf.ManagePortal')
    productUIDs = schema.Dict(
        title=_(u"Product UID(s)"),
        description=_(u"Product UID(s) at shopping cart, include qty."),
        key_type=schema.TextLine(title=u"Key"),
        value_type=schema.Int(title=u"Value"),
        required=False,
    )

    form.write_permission(amount='cmf.ManagePortal')
    amount = schema.Int(
        title=_(u"Amount"),
        description=_(u"Amount"),
        required=True,
    )

    form.write_permission(orderState='cmf.ManagePortal')
    orderState = schema.Choice(
        title=_(u"Order State"),
        description=_(u"Order state."),
        vocabulary=ORDER_STATE,
        default=u'ordered',
        required=True,
    )

    result = schema.Dict(
        title=_(u"Trading Results"),
        description=_(u"Trading Results, feedback from allPay."),
        key_type=schema.TextLine(title=u"Key"),
        value_type=schema.TextLine(title=u"Value"),
        required=False,
    )

    logisticsMapResult = schema.Dict(
        title=_(u"Logistics Map Results"),
        description=_(u"Logistics map results, feedback from allPay."),
        key_type=schema.TextLine(title=u"Key"),
        value_type=schema.TextLine(title=u"Value"),
        required=False,
    )

    logisticsExpressResult = schema.Dict(
        title=_(u"Logistics Express Create Results"),
        description=_(u"Logistics express create results, feedback from allPay."),
        key_type=schema.TextLine(title=u"Key"),
        value_type=schema.TextLine(title=u"Value"),
        required=False,
    )
