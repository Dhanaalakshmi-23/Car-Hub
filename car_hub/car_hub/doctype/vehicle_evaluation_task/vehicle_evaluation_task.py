# Copyright (c) 2026, Dhanaa Lakshmi and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from car_hub.utils.notifications import notify_evaluation_completed


class VehicleEvaluationTask(Document):


    def validate(self):
        self.validate_links()
        self.validate_ratings()
        if frappe.session.user != "Administrator":
            roles = frappe.get_roles(frappe.session.user)
            if "Evaluator" in roles and "Sales Manager" not in roles and "Dealership Admin" not in roles:
                if self.evaluator != frappe.session.user:
                    frappe.throw("You can only edit Evaluation Tasks assigned to you.")
        if self.status == "Completed" and not self.overall_condition_verdict:
            frappe.throw("Please set the Overall Condition Verdict before marking as Completed.")


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
            notify_evaluation_completed(self.name)

    def update_vehicle_inventory(self):
        if not self.vehicle_inventory:
            return
        inv = frappe.get_doc("Vehicle Inventory", self.vehicle_inventory)
        inv.condition_rating = self.map_verdict(self.overall_condition_verdict)
        inv.refurbishment_cost = self.estimated_refurbishment_cost
        inv.expected_selling_price = self.recommended_selling_price
        inv.status = (
            "Written Off"
            if self.overall_condition_verdict == "Not Worth Refurbishing"
            else "Available for Sale"
        )
        notes = f"\n[Evaluation {self.name} on {self.evaluation_date}]: {self.evaluator_notes or ''}"
        inv.vehicle_history_remarks = (inv.vehicle_history_remarks or "") + notes
        inv.save(ignore_permissions=True)

    def map_verdict(self, verdict):
        return {
            "Excellent": "Excellent",
            "Good": "Good",
            "Fair": "Fair",
            "Poor": "Poor",
            "Not Worth Refurbishing": "Poor",
        }.get(verdict, "Fair")
