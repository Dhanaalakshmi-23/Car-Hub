# Copyright (c) 2026, Dhanaa Lakshmi and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from car_hub.utils.notifications import notify_evaluation_completed
from frappe.utils import now_datetime, nowdate,getdate

class VehicleEvaluationTask(Document):
    def on_update(self):
        notify_evaluation_completed(self.name)
    def before_insert(self):
        self.auto_assign_default_checklist()
    
    def validate(self):
        self.validate_links()
        self.validate_ratings()

        # Restrict edits to assigned evaluator
        if frappe.session.user != "Administrator":
            roles = frappe.get_roles(frappe.session.user)
            if "Evaluator" in roles and "Sales Manager" not in roles and "Dealership Admin" not in roles:
                if self.evaluator != frappe.session.user:
                    frappe.throw("You can only edit Evaluation Tasks assigned to you.")

        # Must set overall condition before completing
        if self.status == "Completed" and not self.overall_condition:
            frappe.throw("Please set the Overall Condition before marking as Completed.")

        # Track checklist
        if self.evaluation_checklist:
            all_done = all(row.status == "Completed" for row in self.evaluation_checklist)
            if all_done:
                if not self.completed_on:
                    self.completed_on = now_datetime()

                # Convert due_date to date for comparison
                if self.due_date and getdate(self.completed_on) > getdate(self.due_date):
                    self.status = "Overdue"
                else:
                    self.status = "Completed"

            elif any(row.status == "Completed" for row in self.evaluation_checklist):
                if not self.started_on:
                    self.started_on = now_datetime()
                self.status = "In Progress"

        # If past due date but not completed
        if self.due_date and self.status not in ["Completed", "Overdue"]:
            if getdate(nowdate()) > getdate(self.due_date):
                self.status = "Overdue"
    def auto_assign_default_checklist(self):
        """Auto assign default checklist + assigned_on"""

        if not self.evaluation_checklist:
            default_items = frappe.get_all(
                "Evaluation Checklist",
                fields=["component"]
            )

            for item in default_items:
                self.append("evaluation_checklist", {
                    "component": item.component,
                    "status": "Pending"
                })
        if not self.assigned_on:
            self.assigned_on = now_datetime()
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
            # notify_evaluation_completed(self.name)

    def update_vehicle_inventory(self):
        if not self.vehicle_inventory:
            return
        inv = frappe.get_doc("Vehicle Inventory", self.vehicle_inventory)
        inv.condition_rating = self.map_verdict(self.overall_condition)
        inv.refurbishment_cost = self.refurbishment_cost
        inv.expected_selling_price = self.recommended_price
        inv.status = (
            "Written Off"
            if self.overall_condition == "Not Worth Refurbishing"
            else "Available for Sale"
        )
        notes = f"\n[Evaluation {self.name} on {self.evaluation_duration}]: {self.notes or ''}"
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
    
def get_permission_query_conditions(user):
    if "Evaluator" in frappe.get_roles(user):
        return f"`tabVehicle Evaluation Task`.evaluator = '{user}'"
    return None