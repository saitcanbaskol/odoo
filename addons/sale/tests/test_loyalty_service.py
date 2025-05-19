# addons/sale/tests/test_loyalty_service.py

from odoo.tests.common import TransactionCase
from odoo.exceptions import AccessError
import logging
from odoo.tests import Form, tagged, users
_logger = logging.getLogger(__name__)
_logger.info("TEST LOYALTY IS RUNNING")
@tagged('post_install', '-at_install')
class TestLoyaltyService(TransactionCase):

    def setUp(self):
        super().setUp()
        # Create a test partner with 0 initial loyalty points
        self.partner = self.env['res.partner'].create({
            'name': 'Test Customer',
            'email': 'test@example.com',
            'loyalty_points': 0,
        })

        # Create a test product
        self.product = self.env['product.product'].create({
            'name': 'Test Product',
            'list_price': 100.0,
            'standard_price': 50.0,
            'type': 'consu',
        })

    def test_award_loyalty_points_on_order(self):
        """Test that loyalty points are awarded on order creation"""
        order = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'order_line': [(0, 0, {
                'product_id': self.product.id,
                'product_uom_qty': 1,
                'price_unit': 100.0,
            })],
        })

        order.action_confirm()

        self.partner.invalidate_recordset()  # Refresh record
        self.assertGreater(self.partner.loyalty_points, 0, "Loyalty points were not awarded")

    def test_redeem_loyalty_points(self):
        """Test that loyalty points are redeemed on second order"""
        # Manually give the partner 100 points
        self.partner.loyalty_points = 100

        order = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'order_line': [(0, 0, {
                'product_id': self.product.id,
                'product_uom_qty': 1,
                'price_unit': 100.0,
            })],
        })

        # Should redeem during confirmation
        order.action_confirm()

        self.partner.invalidate_recordset()
        self.assertLess(self.partner.loyalty_points, 100, "Loyalty points were not redeemed")

    def test_no_loyalty_points_for_unlinked_partner(self):
        """Ensure no points are added for unrelated partner"""
        partner_no_loyalty = self.env['res.partner'].create({
            'name': 'No Loyalty',
            'email': 'nolo@example.com',
        })

        order = self.env['sale.order'].create({
            'partner_id': partner_no_loyalty.id,
            'order_line': [(0, 0, {
                'product_id': self.product.id,
                'product_uom_qty': 1,
                'price_unit': 50.0,
            })],
        })

        order.action_confirm()

        partner_no_loyalty.invalidate_recordset()
        self.assertFalse(hasattr(partner_no_loyalty, 'loyalty_points') or partner_no_loyalty.loyalty_points, "Unexpected loyalty points applied")
