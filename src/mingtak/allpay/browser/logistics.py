# -*- coding: utf-8 -* 
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
#from zope.component import getMultiAdapter
from plone import api
from DateTime import DateTime
import random
import transaction
import urllib
import hashlib
from Products.CMFPlone.utils import safe_unicode
import logging


class LogisticsMap(BrowserView):
    """ Logistics map
    """
    logger = logging.getLogger('logistics.Logistics')
    template = ViewPageTemplateFile("template/logistics.pt")

    def __call__(self):
        context = self.context
        request = self.request
        response = request.response
        catalog = context.portal_catalog

        logisticsMapURL = api.portal.get_registry_record('i8d.content.browser.coverSetting.ICoverSetting.logisticsMapURL')
        merchantId = api.portal.get_registry_record('i8d.content.browser.coverSetting.ICoverSetting.merchantID')
        serverReplyURL = api.portal.get_registry_record('i8d.content.browser.coverSetting.ICoverSetting.serverReplyURL')

        self.actionURL = logisticsMapURL
        self.logistics_form = {
            'MerchantID': merchantId,
            'MerchantTradeNo': request.form.get('MerchantTradeNo'),
            'LogisticsType': 'CVS',
            'LogisticsSubType': request.form.get('LogisticsSubType'),
            'IsCollection': 'N', # 代收貨款，待處理
            'ServerReplyURL': serverReplyURL,
#            'Device': 1, # 上網設備，待處理（可以不處理）
        }
        self.keys = self.logistics_form.keys()

        return self.template()


class LogisticsExpressCreate(BrowserView):
    """ Logistics Express Create
    """
    logger = logging.getLogger('logistics.LogisticsExpressCreate')
    template = ViewPageTemplateFile("template/logistics_express_create.pt")

    def encoded_dict(self, in_dict):
        out_dict = {}
        for k, v in in_dict.iteritems():
            if isinstance(v, unicode):
                v = v.encode('utf8')
            elif isinstance(v, str):
                # Must be encoded in UTF-8
                v.decode('utf8')
            out_dict[k] = v
        return out_dict


    def __call__(self):
        context = self.context
        request = self.request
        response = request.response
        catalog = context.portal_catalog
        portal = api.portal.get()

        hashKey = api.portal.get_registry_record('i8d.content.browser.coverSetting.ICoverSetting.logisticsHashKey')
        hashIV = api.portal.get_registry_record('i8d.content.browser.coverSetting.ICoverSetting.logisticsHashIV')
        order = portal['resource']['order'][request.form['merchantTradeNo']]

        logisticsExpressCreateURL = api.portal.get_registry_record('i8d.content.browser.coverSetting.ICoverSetting.logisticsExpressCreateURL')
        merchantID = api.portal.get_registry_record('i8d.content.browser.coverSetting.ICoverSetting.merchantID')
        merchantTradeNo = request.form['merchantTradeNo']
        merchantTradeDate = DateTime().strftime('%Y/%m/%d %H:%M:%S')

#        import pdb; pdb.set_trace()
        logisticsType = 'CVS' # 待處理(店到店），或是可以不處理？
        logisticsSubType = order.logisticsMapResult.get('LogisticsSubType')
        goodsAmount = order.result['TradeAmt']
        collectionAmount = order.result['TradeAmt'] # 待處理（代收金額）
        isCollection = 'N' # 待處理(是否代收）
        goodsName = order.description[0:12]
        senderName = 'i8d.tw'
        senderPhone = '02-28973942'
        senderCellPhone = '0939-586835'
        receiverName = order.receiver
        receiverPhone = order.phone
        receiverCellPhone = order.cellPhone
        receiverEmail = order.email
        tradeDesc = order.description[0:100]
        serverReplyURL = api.portal.get_registry_record('i8d.content.browser.coverSetting.ICoverSetting.serverReplyURL')
        clientReplyURL = api.portal.get_registry_record('i8d.content.browser.coverSetting.ICoverSetting.clientReplyURL')
        logisticsC2CReplyURL = api.portal.get_registry_record('i8d.content.browser.coverSetting.ICoverSetting.logisticsC2CReplyURL')
        receiverStoreID = order.logisticsMapResult['CVSStoreID']

# 全家的resutnstoreid會有錯，先跳過不處理
#        import pdb; pdb.set_trace()
#        if logisticsSubType == 'UNIMARTC2C':
#            returnStoreID = '146403' # 7-11 西安店
#        elif logisticsSubType == 'FAMIC2C':
#            returnStoreID = '14441' # 全家大同店


        self.formDict = {
            'MerchantId': merchantID,
            'MerchantTradeNo': merchantTradeNo,
            'MerchantTradeDate': merchantTradeDate,
            'LogisticsType': logisticsType,
            'LogisticsSubType': logisticsSubType,
            'GoodsAmount': goodsAmount,
            'CollectionAmount': collectionAmount,
            'IsCollection': isCollection,
            'GoodsName': goodsName,
            'SenderName': senderName,
            'SenderPhone': senderPhone,
            'SenderCellPhone': senderCellPhone,
            'ReceiverName': receiverName,
            'ReceiverPhone': receiverPhone,
            'ReceiverCellPhone': receiverCellPhone,
            'ReceiverEmail': receiverEmail,
            'TradeDesc': tradeDesc,
            'ServerReplyURL': serverReplyURL,
            'ClientReplyURL': clientReplyURL,
            'LogisticsC2CReplyURL': logisticsC2CReplyURL,
            'ReceiverStoreID': receiverStoreID,
#            'ReturnStoreID': returnStoreID,
        }

        self.formDict = self.encoded_dict(self.formDict)
        sortedForm = sorted(self.formDict.iteritems())
        sortedForm.insert(0, ('HashKey', hashKey.encode('utf-8')))
        sortedForm.append(('HashIV', hashIV.encode('utf-8')))
        # TODO: 不依賴 pyallpay, 需改寫以下這行
        # urlEncodeString = do_str_replace(urllib.quote(urllib.urlencode(sortedForm), '+%').lower())
        checkMacValue = hashlib.md5(urlEncodeString).hexdigest().upper()

        self.formDict['CheckMacValue'] = checkMacValue
        self.keys = self.formDict.keys()
        self.actionURL = api.portal.get_registry_record('i8d.content.browser.coverSetting.ICoverSetting.logisticsExpressCreateURL')
        return self.template()


class LogisticsReply(BrowserView):
    """ Logistics Reply
    """
    logger = logging.getLogger('logistics.LogisticsReply')
#    template = ViewPageTemplateFile("template/client_back_url.pt")

    def __call__(self):
        context = self.context
        request = self.request
        response = request.response
        catalog = context.portal_catalog

        brain = catalog({'Type': 'Order', 'id': request.form['MerchantTradeNo']})
        if not brain:
            return

        order = brain[0].getObject()
        if not order.logisticsMapResult:
            order.logisticsMapResult = {}

        for key in request.form.keys():
            order.logisticsMapResult[key] = request.form[key]

        transaction.commit()
        response.redirect('/logistics_express_create?merchantTradeNo=%s' % request.form['MerchantTradeNo'])
        return


class LogisticsClientReply(BrowserView):
    """ Logistics Client Reply, 訂單由系統向allpay發送建立，建立完成將information回傳到這裏
    """
    logger = logging.getLogger('logistics.LogisticsClientReply')
    template = ViewPageTemplateFile("template/logistics_client_reply.pt")

    def __call__(self):
        context = self.context
        request = self.request
        response = request.response
        catalog = context.portal_catalog

        brain = catalog({'Type': 'Order', 'id': request.form['MerchantTradeNo']})
        if not brain:
            return

        order = brain[0].getObject()
        if not order.logisticsExpressResult:
            order.logisticsExpressResult = {}

        for key in request.form.keys():
            order.logisticsExpressResult[key] = request.form[key]

        transaction.commit()
        return self.template()


class LogisticsServerReply(BrowserView):
    """ Logistics Reply, Express Crate feedback，訂單完成後，若訂單狀態有更新，allpay會發送狀態到這裏
    """
    logger = logging.getLogger('logistics.LogisticsServerReply')

    def __call__(self):
        context = self.context
        request = self.request
        response = request.response
        catalog = context.portal_catalog


        brain = catalog({'Type': 'Order', 'id': request.form['MerchantTradeNo']})
        if not brain:
            return

        order = brain[0].getObject()
        if not order.logisticsExpressResult:
            order.logisticsExpressResult = {}

        for key in request.form.keys():
            order.logisticsExpressResult[key] = request.form[key]

        transaction.commit()
#        response.redirect('/logistics_express_create?merchantTradeNo=%s' % request.form['MerchantTradeNo'])
        return

