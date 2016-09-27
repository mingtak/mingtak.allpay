from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from DateTime import DateTime
import transaction
import csv
import json


class UpdateCartState(BrowserView):
    """ Update Cart State
    """

    index = ViewPageTemplateFile("template/update_cart_state.pt")

    def getCartItems(self):
        context = self.context
        request = self.request

        self.itemInCart = json.loads(request.cookies.get('itemInCart', '{}'))
        brain = api.content.find(Type='Product', UID=self.itemInCart.keys())
        return brain


    def __call__(self):
        return self.index()


class AllpayMacro(BrowserView):
    """ Allpay Macro
    """


class OrderView(BrowserView):
    """ Order View
    """


class ShippingMethodHomeAddress(BrowserView):
    """ Shipping Method Home Address
    """
    index = ViewPageTemplateFile("template/shipping_method_home_address.pt")

    def __call__(self):

        context = self.context
        request = self.request
        response = request.response
        portal = api.portal.get()

        if api.user.is_anonymous():
            self.profile = None
        else:
            currentId = api.user.get_current().getId()
            self.profile = portal['members'][currentId]

        return self.index()


class ShippingMethod(BrowserView):
    """ Shipping Method
    """
    index = ViewPageTemplateFile("template/shipping_method.pt")

    def __call__(self):

        context = self.context
        request = self.request
        response = request.response
        portal = api.portal.get()

        if api.user.is_anonymous():
            self.profile = None
        else:
            currentId = api.user.get_current().getId()
            self.profile = portal['members'][currentId]

        return self.index()


class InvoiceMethod(BrowserView):
    """ Invoice Method
    """
