# Copyright (c) 2026, Dhanaa Lakshmi and contributors
# For license information, please see license.txt

from pydoc import doc

import frappe
from frappe.model.document import Document
from datetime import datetime


class VehicleAcquisition(Document):

    def autoname(self):
        date_part = datetime.now().strftime("%Y%m%d")
        self.name = f"VA-{date_part}-{frappe.generate_hash(length=4)}"

    def before_insert(self):
        if self.amended_from:
            self.status = "Amended"
        else:
            self.status = "Draft"

    def validate(self):
        self.validate_seller()
        self.validate_vehicles()
        self.calculate_totals()

    def on_submit(self):
        self.status = "Finalized"
        self.create_vehicle_inventory()
        frappe.db.commit()
        self.update_seller_history()
        self.create_evaluation_tasks()

    def on_cancel(self):
        self.status = "Cancelled"
        self.update_inventory_status_cancel()
        self.update_seller_history_cancel()

        
    def validate_seller(self):
        if not self.seller:
            frappe.throw("Seller is required")

        seller = frappe.db.get_value(
            "Seller Registry",
            self.seller,
            ["seller_name", "phone_number", "seller_type", "is_blacklisted"],
            as_dict=True
        )
        if seller.is_blacklisted:
            frappe.throw("This seller is blacklisted. Cannot proceed.")

        # Auto fetch
        self.seller_name = seller.seller_name
        self.phone_number = seller.phone_number
        self.seller_type = seller.seller_type

    def validate_vehicles(self):
        if not self.vehicles:
            frappe.throw("At least one vehicle is required")

        reg_numbers = set()

        for v in self.vehicles:

            if not v.registration_number:
                frappe.throw("Registration Number is required")

            if v.registration_number in reg_numbers:
                frappe.throw(f"Duplicate registration number: {v.registration_number}")

            if not v.purchase_price or v.purchase_price <= 0:
                frappe.throw(f"Invalid purchase price for {v.registration_number}")

            reg_numbers.add(v.registration_number)

    def calculate_totals(self):

        # Total Purchase Cost
        self.total_purchase_cost = sum(v.purchase_price for v in self.vehicles)

        settings = frappe.get_single("Dealership Settings")

        # Defaults
        if not self.documentation_fees:
            self.documentation_fees = settings.default_documentation_charges or 0

    
        self.transportation_charges = self.transportation_charges or 0
        self.advance_paid = self.advance_paid or 0


        # Grand Total
        self.grand_total = (
            self.total_purchase_cost
            + self.transportation_charges
            + self.documentation_fees
            - self.advance_paid
        )


    def create_vehicle_inventory(self):
        self.inventory_map = {}
        for v in self.vehicles:
            existing = frappe.db.exists("Vehicle Inventory", {
                "registration_number": v.registration_number
            })

            if existing:
                self.inventory_map[v.registration_number] = existing
                continue
            doc = frappe.get_doc({
                "doctype": "Vehicle Inventory",

                # Core Fields
                "registration_number": v.registration_number,
                "manufacturer": v.manufacturer or "m7blh4csdi",
                "model": v.model,
                "year_of_manufacture": v.year,
                "fuel_type": v.fuel_type,
                "transmission_type": v.transmission_type,
                "odometer_reading": v.odometer_reading,
                "acquisition_cost": v.purchase_price,
                "acquisition_reference": self.name,
                "number_of_previous_owners": v.previous_owners,
                "status": "In Evaluation",
            }).insert(ignore_permissions=True, ignore_mandatory=True)
            self.inventory_map[v.registration_number] = doc.name    
    def update_seller_history(self):
        if not self.seller:
            return

        seller = frappe.get_doc("Seller Registry", self.seller)

        for v in self.vehicles:
            # Get correct Vehicle Inventory doc name
            inventory_name = self.inventory_map.get(v.registration_number)

            if not inventory_name:
                continue

            # Check for duplicate entry
            exists = False
            for row in seller.vehicle_history:
                if (
                    row.vehicle == inventory_name and
                    row.acquisition_reference == self.name
                ):
                    exists = True
                    break

            # Append only if not exists
            if not exists:
                seller.append("vehicle_history", {
                    "vehicle": inventory_name,                    
                    "acquisition_reference": self.name,           
                    "acquisition_date": self.acquisition_date,   
                    "acquisition_cost": v.purchase_price,
                })

        seller.save(ignore_permissions=True)

    def update_inventory_status_cancel(self):
        for v in self.vehicles:
            inventory_name = self.get_inventory_name(v.registration_number)
            if not inventory_name:
                frappe.log_error(f"Inventory not found for {v.registration_number}")
                continue

            doc = frappe.get_doc("Vehicle Inventory", inventory_name)
            doc.status = "Written Off"
            doc.save(ignore_permissions=True)


    def update_seller_history_cancel(self):
        if not self.seller:
            return

        rows = frappe.get_all(
            "Seller Vehicle History",
            filters={"parent": self.seller},
            pluck="name"
        )

        if not rows:
            frappe.log_error(f"No seller vehicle history found for {self.seller}")
            return

        for row_name in rows:
            doc = frappe.get_doc("Seller Vehicle History", row_name)
            doc.status = "Cancelled"
            doc.save(ignore_permissions=True)

    def get_inventory_name(self, reg_no):
        name = frappe.db.get_value(
            "Vehicle Inventory",
            {
                "registration_number": reg_no,
                "acquisition_reference": self.name
            },
            "name"
        )

        
        return name

    def create_evaluation_tasks(self):
        settings = frappe.get_single("Dealership Settings")

        if not settings.auto_create_evaluation_task:
            return

        # Get all evaluators
        evaluators = frappe.get_all(
            "Has Role",
            filters={"role": "Evaluator"},
            pluck="parent"
        )
        evaluators = [e for e in evaluators if "@" in e]

        if not evaluators:
            frappe.throw("No evaluators available")

        last = settings.last_evaluator
        index = (evaluators.index(last) + 1) % len(evaluators) if last in evaluators else 0
        last_used = None

        # Define your 8 default checklist items
        default_checklist = [
            {"check_item": "Engine Condition"},
            {"check_item": "Transmission"},
            {"check_item": "Brakes"},
            {"check_item": "Suspension"},
            {"check_item": "Tires & Wheels"},
            {"check_item": "Lights & Indicators"},
            {"check_item": "Interior Condition"},
            {"check_item": "Exterior Condition"},
        ]

        for v in self.vehicles:
            inventory = self.inventory_map.get(v.registration_number)
            if not inventory:
                continue

            selected = evaluators[index]

            # Create task with only 8 checklist items
            frappe.get_doc({
                "doctype": "Vehicle Evaluation Task",
                "vehicle_acquisition": self.name,
                "vehicle_inventory": inventory,
                "evaluator": selected,
                "status": "Pending",
                "evaluation_checklist": default_checklist
            }).insert(ignore_permissions=True)

            last_used = selected
            index = (index + 1) % len(evaluators)

        if last_used:
            frappe.db.set_single_value("Dealership Settings", "last_evaluator", last_used)