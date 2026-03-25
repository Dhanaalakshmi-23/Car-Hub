# Copyright (c) 2026, Dhanaa Lakshmi and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class VehicleEvaluationTask(Document):


    def validate(self):
        self.validate_links()
        self.validate_ratings()


    def validate_links(self):
        if not self.vehicle_acquisition:
            frappe.throw("Vehicle Acquisition is required")

        if not self.vehicle_inventory:
            frappe.throw("Vehicle Inventory is required")


    def validate_ratings(self):
        for row in self.evaluation_checklist:
            if row.rating and (row.rating < 1 or row.rating > 5):
                frappe.throw(f"Rating must be between 1 and 5 for {row.component}")

    def on_update(self):
        if self.status == "Completed":
            self.update_vehicle_inventory()


