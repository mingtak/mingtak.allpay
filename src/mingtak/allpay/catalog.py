# -*- coding: utf-8 -*-
from plone.indexer.decorator import indexer
from mingtak.allpay.interfaces import IOrder


@indexer(IOrder)
def productUIDs_indexer(obj):
    return obj.productUIDs

@indexer(IOrder)
def amount_indexer(obj):
    return obj.amount

@indexer(IOrder)
def orderState_indexer(obj):
    return obj.orderState
