# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, fields, api, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    automatic_group_sale_order_at_save = fields.Boolean('Group sales order automatically at save', default=True,
                                                        readonly=True,
                                                        states={'draft': [('readonly', False)],
                                                                'sent': [('readonly', False)]},
                                                        help='Regroup automatically sales order lines.')

    @api.model
    def create(self, values):
        if values.get("automatic_group_sale_order_at_save", self.automatic_group_sale_order_at_save) and \
                "order_line" in values.keys():
            # regroup lines order, add section and ignore new section
            lst_order_line = self._write_list_ordered_by_service(values)
            values["order_line"] = lst_order_line

        result = super(SaleOrder, self).create(values)
        return result

    @api.multi
    def write(self, values):
        if values.get("automatic_group_sale_order_at_save", self.automatic_group_sale_order_at_save) and \
                "order_line" in values.keys():
            # regroup lines order, add section and ignore new section
            lst_order_line = self._write_list_ordered_by_service(values)
            values["order_line"] = lst_order_line

        result = super(SaleOrder, self).write(values)
        return result

    @staticmethod
    def get_material_name():
        return _("Material")

    @staticmethod
    def get_work_load_name():
        return _("Work load")

    def _write_list_ordered_by_service(self, values):
        # Supported case
        # create with only product and service
        # create with product, service, note and supported and unsupported sections
        # write with reordered product and service
        # write with new product or service
        # write with deleted product, service, note and section
        # write with modify product or service
        find_label_material = False
        find_label_service = False
        lst_order_line = []
        lst_service = []
        lst_product = []
        lst_other = []
        dct_note = {}
        lst_deleted_order = []

        def _add_line_note(i):
            j = i - 1
            while j in [a[2] for a in lst_deleted_order]:
                j -= 1
            if j < 0 and -1 in dct_note.keys():
                lst_other.append([line, order_line, i])
            else:
                dct_note[j] = [line, order_line, i]

        def _add_line_product(i, line, product_id):
            product = self.env['product.product'].browse(product_id)
            if product.type == "service":
                lst_service.append([line, product, i])
            elif product.type == "consu" or product.type == "product":
                lst_product.append([line, product, i])
            else:
                lst_other.append([line, product, i])

        def _add_order_line(line, new_sequence_index):
            index = new_sequence_index + 1
            item = self._prepare_sale_order_line_sequence(line, index)
            lst_order_line.append(item)

            # adding a note
            while line[2] in dct_note.keys():
                index += 1
                item = self._prepare_sale_order_line_sequence(dct_note[line[2]], index)
                lst_order_line.append(item)
                # good hack to support a note under a note with recursive line with note
                if line[2] in dct_note.keys():
                    line = dct_note[line[2]]
            return index

        # Regroup information
        i = -1
        for a_line in values.get("order_line", []):
            i += 1
            line = [a for a in a_line]

            # Ignore this if deleted
            if line[0] in (2, 3, 5):
                lst_deleted_order.append([line, False, i])
                continue

            order_line = None
            if type(line[1]) is int and line[0] != 0:
                # already recorded
                order_line = self.env['sale.order.line'].browse(line[1])
                if order_line.display_type:
                    if order_line.display_type == "line_section":
                        # support update
                        if line[2] and "name" in line[2]:
                            order_line_name = line[2].get("name")
                        else:
                            order_line_name = order_line.name

                        if order_line_name == self.get_material_name():
                            if find_label_material:
                                # delete it
                                line[0] = 2
                                lst_deleted_order.append([line, order_line, i])
                                continue
                            lst_product.insert(0, [line, order_line, i])
                            find_label_material = True
                        elif order_line_name == self.get_work_load_name():
                            if find_label_service:
                                # delete it
                                line[0] = 2
                                lst_deleted_order.append([line, order_line, i])
                                continue
                            lst_service.insert(0, [line, order_line, i])
                            find_label_service = True
                        else:
                            lst_other.append([line, order_line, i])
                    elif order_line.display_type == "line_note":
                        _add_line_note(i)
                    else:
                        lst_other.append([line, order_line, i])
                elif line[0] in [1, 6] and "product_id" in line[2]:
                    # detect if product has changed
                    product_id = line[2].get("product_id")
                    _add_line_product(i, line, product_id)
                elif order_line.product_id.type == "service":
                    lst_service.append([line, order_line, i])
                elif order_line.product_id.type == "consu" or order_line.product_id.type == "product":
                    lst_product.append([line, order_line, i])
                else:
                    lst_other.append([line, order_line, i])
            else:
                # new line order
                info = line[2]
                if info and "display_type" in info and not info.get("display_type"):
                    product_id = info.get("product_id")
                    _add_line_product(i, line, product_id)
                elif info and "display_type" in info and info.get("display_type") == "line_note":
                    _add_line_note(i)
                else:
                    if line[2].get("name") == self.get_material_name():
                        if find_label_material:
                            # Ignore duplication
                            continue
                        find_label_material = True
                        lst_product.insert(0, [line, False, i])
                    elif line[2].get("name") == self.get_work_load_name():
                        if find_label_service:
                            # Ignore duplication
                            continue
                        find_label_service = True
                        lst_service.insert(0, [line, False, i])
                    else:
                        lst_other.append([line, False, i])

        # Create label
        new_sequence_index = 10

        # Create new list with ordered items
        # Material section
        if not find_label_material:
            dct_line_section = {"name": self.get_material_name(), "display_type": "line_section",
                                "sequence": new_sequence_index}
            item_line_section = [0, "virtual_112", dct_line_section]
            lst_order_line.append(item_line_section)

            # adding a note
            if -1 in dct_note.keys():
                new_sequence_index += 1
                item = self._prepare_sale_order_line_sequence(dct_note[-1], new_sequence_index)
                lst_order_line.append(item)

        for line in lst_product:
            new_sequence_index = _add_order_line(line, new_sequence_index)

        # Service section
        if not find_label_service:
            new_sequence_index += 1
            dct_line_section = {"name": self.get_work_load_name(), "display_type": "line_section",
                                "sequence": new_sequence_index}
            item_line_section = [0, "virtual_113", dct_line_section]
            lst_order_line.append(item_line_section)

        for line in lst_service:
            new_sequence_index = _add_order_line(line, new_sequence_index)

        # Other section
        for line in lst_other:
            new_sequence_index = _add_order_line(line, new_sequence_index)

        # Deleted section will disappear automatically
        for line in lst_deleted_order:
            lst_order_line.append(line[0])

        return lst_order_line

    def _prepare_sale_order_line_sequence(self, line, new_sequence_index):
        if line[0][2] is False:
            # force write value
            line[0][2] = {}
        line[0][2]["sequence"] = new_sequence_index
        # force write value if different sequence
        if line[1] and isinstance(line[1], self.env["sale.order.line"].__class__):
            if line[1].sequence != new_sequence_index:
                line[0][0] = 1
        return line[0]
