# Copyright (c) 2026, Dhanaa Lakshmi and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime


class VehicleAcquisition(Document):

    def autoname(self):
        date_part = datetime.now().strftime("%Y%m%d")
        self.name = f"VA-{date_part}-{frappe.generate_hash(length=4)}"

    def before_insert(self):
        self.assign_evaluator()

        if self.amended_from:
            self.status = "Amended"

    def validate(self):
        self.validate_seller()
        self.validate_vehicles()
        self.calculate_totals()

    def on_submit(self):
        self.create_vehicle_inventory()
        self.update_seller_history()
        self.create_evaluation_tasks()

    def on_cancel(self):
        if not self.cancellation_reason:
            frappe.throw("Cancellation reason is required")

        self.update_inventory_status_cancel()
        self.update_seller_history_cancel()

    def validate_seller(self):
        if not self.seller:
            frappe.throw("Seller is required")

        seller = frappe.get_doc("Seller Registry", self.seller)

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

    def assign_evaluator(self):
        if self.evaluator:
            return

        evaluators = frappe.get_all(
            "Has Role",
            filters={"role": "Evaluator"},
            pluck="parent"
        )

        if not evaluators:
            frappe.throw("No evaluators available")

        last = frappe.db.get_single_value("Dealership Settings", "last_evaluator")

        if last in evaluators:
            index = (evaluators.index(last) + 1) % len(evaluators)
        else:
            index = 0

        selected = evaluators[index]

        self.evaluator = selected

        frappe.db.set_single_value("Dealership Settings", "last_evaluator", selected)

    def calculate_totals(self):

        # Total Purchase Cost
        self.total_purchase_cost = sum(v.purchase_price for v in self.vehicles)

        settings = frappe.get_single("Dealership Settings")

        # Defaults
        if not self.documentation_fees:
            self.documentation_fees = settings.default_documentation_fee or 0

        if not self.tax_percentage:
            self.tax_percentage = settings.tax_percentage or 0

        self.transportation_charges = self.transportation_charges or 0
        self.advance_paid = self.advance_paid or 0

        # Tax
        self.tax_amount = (self.total_purchase_cost * self.tax_percentage) / 100

        # Grand Total
        self.grand_total = (
            self.total_purchase_cost
            + self.transportation_charges
            + self.documentation_fees
            + self.tax_amount
            - self.advance_paid
        )


    def create_vehicle_inventory(self):
        for v in self.vehicles:
            existing = frappe.db.exists("Vehicle Inventory", {
                "registration_number": v.registration_number
            })

            if existing:
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
                "odometerkm": v.odometer_reading,
                "number_of_previous_owner": v.number_of_previous_owners,
                "acquisition_cost": v.total_purchase_cost,
                "acquisition_reference": self.name,
                "status": "In Evaluation",
            })
            doc.insert(ignore_permissions=True, ignore_mandatory=True)

    def update_seller_history(self):
        seller = frappe.get_doc("Seller Registry", self.seller)

        for v in self.vehicles:
            seller.append("vehicle_history", {
                "vehicle": v.registration_number,
                "acquisition": self.name,
                "date": self.acquisition_date,
                "price": v.total_purchase_cost,
            })

        seller.save(ignore_permissions=True)

    def update_inventory_status_cancel(self):
        for v in self.vehicles:
            inventory_name = self.get_inventory_name(v.registration_number)

            if inventory_name:
                doc = frappe.get_doc("Vehicle Inventory", inventory_name)
                doc.status = "Written Off"
                doc.save(ignore_permissions=True)

    def update_seller_history_cancel(self):
        seller = frappe.get_doc("Seller Registry", self.seller)

        for row in seller.vehicle_history:
            if row.acquisition == self.name:
                row.status = "Cancelled"

        seller.save(ignore_permissions=True)

    def get_inventory_name(self, reg_no):
        return frappe.db.get_value(
            "Vehicle Inventory",
            {
                "registration_number": reg_no,
                "acquisition_reference": self.name
            },
            "name"
        )

    def create_evaluation_tasks(self):

        settings = frappe.get_single("Dealership Settings")

        if not settings.auto_create_evaluation_task:
            return

        evaluators = frappe.get_all(
            "Has Role",
            filters={"role": "Evaluator"},
            pluck="parent"
        )

        if not evaluators:
            frappe.throw("No evaluators available")

        last = settings.last_evaluator

        # Start from next evaluator
        if last in evaluators:
            index = (evaluators.index(last) + 1) % len(evaluators)
        else:
            index = 0

        last_used = None

        for v in self.vehicles:
            selected = evaluators[index]

            frappe.get_doc({
                "doctype": "Vehicle Evaluation Task",
                "vehicle_acquisition": self.name,
                "vehicle_inventory": self.get_inventory_name(v.registration_number),
                "evaluator": selected,
                "status": "Pending"
            }).insert(ignore_permissions=True)

            last_used = selected

            index = (index + 1) % len(evaluators)

        if last_used:
            frappe.db.set_single_value("Dealership Settings", "last_evaluator", last_used)