# -*- coding: utf-8 -*
from mingtak.allpay import _
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
#from zope.component import getMultiAdapter

from z3c.relationfield.relation import RelationValue
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent

from plone import api
#from pyallpay import AllPay
from DateTime import DateTime
import random
import transaction
import json
import logging


class ReturnUrl(BrowserView):
    """ Return URL
    """

    def __call__(self):
        context = self.context
        request = self.request
        response = request.response
        catalog = context.portal_catalog
        itemInCart = request.cookies.get('itemInCart', '')
        itemInCart_list = itemInCart.split()

        with api.env.adopt_user(username="admin"):
            if not request.form['MerchantTradeNo']:
                return
            try:
                order = catalog({'Type':'Order', 'Title':request.form['MerchantTradeNo']})[0].getObject()
            except:
                return

            if not order.result:
                order.result = {}

            for key in request.form.keys():
                order.result[key] = request.form[key]

            transaction.commit()
            return


class ClientBackUrl(BrowserView):
    """ Client back url
    """

    template = ViewPageTemplateFile("template/client_back_url.pt")
    def __call__(self):
        context = self.context
        request = self.request
        response = request.response
        catalog = context.portal_catalog
        portal = api.portal.get()
#        itemInCart = request.cookies.get('itemInCart', '')
#        itemInCart_list = itemInCart.split()

        response.setCookie('itemInCart', '')
#        response.redirect('/logistics_map?MerchantTradeNo=%s' % request.form['MerchantTradeNo'])

        self.order = catalog({'Type':'Order', 'id':request.form['MerchantTradeNo']})[0]
        self.products = catalog({'Type':'Product', 'UID':self.order.productUIDs.keys()})
        if request.form.get('LogisticsType') == 'cvs':
            response.redirect('%s/logistics_map?MerchantTradeNo=%s&LogisticsType=%s&LogisticsSubType=%s' %
                (portal.absolute_url(), request.form.get('MerchantTradeNo'), request.form.get('LogisticsType'), request.form.get('LogisticsSubType'))
            )
            return

        # 計算佣金(聯盟行銷, 預設10%)
        self.orderTotal = self.order.getObject().amount
        if self.orderTotal:
            self.revenue = int(self.orderTotal * 0.10)
        else:
            self.revenue = 0

        self.traceCode = " \
            VA.remoteLoad({ \
                whiteLabel: { id: 8, siteId: 1193, domain: 'vbtrax.com' }, \
                conversion: true, \
                conversionData: { \
                    step: 'sale', \
                    revenue: '%s', \
                    orderTotal: '%s', \
                    order: '%s', \
                }, \
                locale: 'en-US', mkt: true \
            }); \
        " % (self.revenue, self.orderTotal, self.order.id)

        return self.template()


class CheckoutConfirm(BrowserView):
    """ Checkout Confirm
    """

    logger = logging.getLogger('bill.Checkout')
    template = ViewPageTemplateFile("template/checkout_confirm.pt")
    home_template = ViewPageTemplateFile("template/home_template.pt")
    cvs_template = ViewPageTemplateFile("template/cvs_template.pt")

    def get_home_template(self):
        return self.home_template()


    def get_cvs_template(self):
        return self.cvs_template()


    def __call__(self):
        context = self.context
        request = self.request
        response = request.response
        catalog = context.portal_catalog
        portal = api.portal.get()

        if api.user.is_anonymous():
            self.profile = None
#            response.redirect('/')
#            return
        else:
            currentId = api.user.get_current().getId()
            self.profile = portal['members'][currentId]

        self.itemInCart = request.cookies.get('itemInCart', '')
        self.itemInCart = json.loads(self.itemInCart)
        self.brain = catalog({'UID':self.itemInCart.keys()})

        self.shippingFee = 0
        self.discount = 0
        self.totalAmount = 0
        for item in self.brain:
            qty = self.itemInCart[item.UID]
            self.totalAmount += item.salePrice * qty
            self.shippingFee += item.standardShippingCost # 同品項只收一次運費(ex, item_1, qty=3, 運費也只收一筆)
            self.discount += (item.salePrice * item.maxUsedBonus * qty)

        if self.profile and self.discount > self.profile.bonus:
            self.discount = self.profile.bonus

        self.payable = self.totalAmount
        self.payable += self.shippingFee
        # 尚未減 discount , 放在 view 顯示

        return self.template()


class Checkout(BrowserView):
    """ Checkout
    """

    logger = logging.getLogger('bill.Checkout')

    def __call__(self):
        context = self.context
        request = self.request
        response = request.response
        catalog = context.portal_catalog
        portal = api.portal.get()
        itemInCart = request.cookies.get('itemInCart', '')
        itemInCart = json.loads(itemInCart)

        # 檢查收件地址
        if request.form.get('LogisticsType') == 'home' and not request.form.get('address'):
            api.portal.show_message(message=_(u'Please fill full address information'), request=request, type='error')
            response.redirect('%s/@@checkout_confirm' % portal.absolute_url())
            return

        if api.user.is_anonymous():
            profile = None
        else:
            currentId = api.user.get_current().getId()
            profile = portal['members'][currentId]

        brain = catalog({'UID':itemInCart.keys()})
        totalAmount = 0
        itemName = ''
        itemDescription = ''
#        productUIDs = {}
        shippingFee = 0
        discount = 0
        specialDiscount = 0 # 未來促銷活動可用

        for item in brain:
            qty = itemInCart.get(item.UID, 1)
            totalAmount += item.salePrice * qty
            itemName += '%s $%s X %s#' % (item.Title, item.salePrice, qty)
            itemDescription += '%s: $%s X %s || ' % (item.Title, item.salePrice, qty)

#            shippingFee += item.standardShippingCost # 同品項只收一次運費(ex, item_1, qty=3, 運費也只收一筆)
            shippingFee = 0 # 目前全館免運費
            if not api.user.is_anonymous():
                discount += int(item.salePrice * item.maxUsedBonus) * int(request.cookies.get(item.UID, 1))

        totalAmount += shippingFee

        if profile:
            if request.form.get('usingbonus', 'n') == 'n':
                discount = 0
            if discount > profile.bonus:
                discount = profile.bonus
            totalAmount -= discount

            # 折抵 Special Discount
            totalAmount -= specialDiscount

            itemName += 'shipping Fee: %s, discount: %s' % (shippingFee, discount)
            itemDescription += 'shipping Fee: %s, discount: %s' % (shippingFee, discount)

            # Special Discount資訊
            if specialDiscount > 0:
                itemName += ', Special Discount: %s' % (specialDiscount)
                itemDescription += ', Special Discount: %s' % (specialDiscount)
        else:
            itemName += 'shipping Fee: %s' % (shippingFee)
            itemDescription += 'shipping Fee: %s' % (shippingFee)

            # 折抵 Special Discount
            totalAmount -= specialDiscount
            # Special Discount資訊
            if specialDiscount > 0:
                itemName += ', Special Discount: %s' % (specialDiscount)
                itemDescription += ', Special Discount: %s' % (specialDiscount)

        import pdb; pdb.set_trace()

        merchantTradeNo = '%s_%s' % (DateTime().strftime('%Y%m%d%H%M%S'), random.randint(10000,99999))

        with api.env.adopt_roles(['Manager']):
#            import pdb ;pdb.set_trace()
            order = api.content.create(
                type='Order',
                title=merchantTradeNo,
                description = '%s, Total: $%s' % (itemDescription, totalAmount),
                productUIDs = itemInCart,
                amount = totalAmount,
                receiver = request.form.get('receiver', ''),
                phone = request.form.get('phone', ''),
                cellPhone = request.form.get('cellphone', ''),
                email = request.form.get('email',''),
                addr_city = request.form.get('city', ''),
                addr_district = request.form.get('district', ''),
                addr_zip = request.form.get('zipcode', ''),
                addr_address = request.form.get('address', ''),
                taxId = request.form.get('taxid', ''),
                companyTitle = request.form.get('companytitle', ''),
                container=portal['resource']['order'],
            )

            if profile:
                profile.bonus -= discount
            else:
                api.content.transition(obj=order, transition='publish')

            transaction.commit()

        paymentInfoURL = api.portal.get_registry_record('i8d.content.browser.coverSetting.ICoverSetting.paymentInfoURL')
        clientBackURL = api.portal.get_registry_record('i8d.content.browser.coverSetting.ICoverSetting.clientBackURL')
        payment_info = {'TotalAmount': totalAmount,
                        'ChoosePayment': 'ALL',
                        'MerchantTradeNo': merchantTradeNo,
                        'ItemName': itemName,
                        'PaymentInfoURL': paymentInfoURL,
                        'ClientBackURL': '%s?MerchantTradeNo=%s&LogisticsType=%s&LogisticsSubType=%s' %
                            (clientBackURL, merchantTradeNo, request.form.get('LogisticsType', 'cvs'), request.form.get('LogisticsSubType', 'UNIMART')),  #可以使用 get 帶參數
        }
        # TODO: 不依賴 pyallpay, 下面的 ALLPay(payment_info)需改寫
        # ap = AllPay(payment_info)
        # check out, this will return a dictionary containing checkValue...etc.
        dict_url = ap.check_out()
        # generate the submit form html.
        form_html = ap.gen_check_out_form(dict_url)

        return form_html

