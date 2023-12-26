# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, fields, models


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    # def _get_global_route_rules_values(self):
    #     rules = super(StockWarehouse, self)._get_global_route_rules_values()
    #     subcontract_location_id = self._get_subcontracting_location()
    #     rules.update({
    #         'subcontracting_mto_pull_id': {
    #             'depends': ['subcontracting_to_resupply'],
    #             'create_values': {
    #                 'procure_method': 'make_to_order',
    #                 'company_id': self.company_id.id,
    #                 'action': 'pull',
    #                 'auto': 'manual',
    #                 'route_id': self._find_global_route('fms_core.route_resupply_subcontractor_mto', _('Make To Order')).id,
    #                 'name': self._format_rulename(self.lot_stock_id, subcontract_location_id, 'MTO'),
    #                 'location_dest_id': self.lot_stock_id.id,
    #                 'location_src_id': subcontract_location_id.id,
    #                 'picking_type_id': self.subcontracting_resupply_type_id.id
    #             },
    #             'update_values': {
    #                 'active': self.subcontracting_to_resupply
    #             }
    #         }
    #     })
    #     return rules
