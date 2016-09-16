# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import mingtak.allpay


class MingtakAllpayLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        self.loadZCML(package=mingtak.allpay)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'mingtak.allpay:default')


MINGTAK_ALLPAY_FIXTURE = MingtakAllpayLayer()


MINGTAK_ALLPAY_INTEGRATION_TESTING = IntegrationTesting(
    bases=(MINGTAK_ALLPAY_FIXTURE,),
    name='MingtakAllpayLayer:IntegrationTesting'
)


MINGTAK_ALLPAY_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(MINGTAK_ALLPAY_FIXTURE,),
    name='MingtakAllpayLayer:FunctionalTesting'
)


MINGTAK_ALLPAY_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        MINGTAK_ALLPAY_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE
    ),
    name='MingtakAllpayLayer:AcceptanceTesting'
)
