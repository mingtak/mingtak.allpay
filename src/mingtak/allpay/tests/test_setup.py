# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from mingtak.allpay.testing import MINGTAK_ALLPAY_INTEGRATION_TESTING  # noqa
from plone import api

import unittest


class TestSetup(unittest.TestCase):
    """Test that mingtak.allpay is properly installed."""

    layer = MINGTAK_ALLPAY_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if mingtak.allpay is installed."""
        self.assertTrue(self.installer.isProductInstalled(
            'mingtak.allpay'))

    def test_browserlayer(self):
        """Test that IMingtakAllpayLayer is registered."""
        from mingtak.allpay.interfaces import (
            IMingtakAllpayLayer)
        from plone.browserlayer import utils
        self.assertIn(IMingtakAllpayLayer, utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = MINGTAK_ALLPAY_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')
        self.installer.uninstallProducts(['mingtak.allpay'])

    def test_product_uninstalled(self):
        """Test if mingtak.allpay is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled(
            'mingtak.allpay'))

    def test_browserlayer_removed(self):
        """Test that IMingtakAllpayLayer is removed."""
        from mingtak.allpay.interfaces import IMingtakAllpayLayer
        from plone.browserlayer import utils
        self.assertNotIn(IMingtakAllpayLayer, utils.registered_layers())
