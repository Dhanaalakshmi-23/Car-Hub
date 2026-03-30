# Copyright (c) 2026, Dhanaa Lakshmi and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime


class VehicleInventory(Document):

	def validate(self):
		self.validate_mandatory_fields()
		self.validate_registration()
		self.validate_year()
		self.validate_numbers()
		self.calculate_total_investment()
		self.validate_prices()
		self.check_profit_margin()
		self.validate_leaf_category()
		self.set_condition_auto()

	def after_insert(self):
		# Trigger background job after first save
		frappe.enqueue( # NOtification - 1
			"car_hub.car_hub.doctype.vehicle_inventory.vehicle_inventory.notify_customers",
			vehicle=self.name
		)

	def validate_mandatory_fields(self):
		if not self.registration_number:
			frappe.throw("Registration Number is mandatory")

		if not self.manufacturer:
			frappe.throw("Manufacturer is mandatory")

		if not self.vehicle_classification:
			frappe.throw("Vehicle Classification is mandatory")

		if not self.acquisition_cost:
			frappe.throw("Acquisition Cost is mandatory")



	def validate_registration(self):
		if frappe.db.exists("Vehicle Inventory", {
			"registration_number": self.registration_number,
			"name": ["!=", self.name]
		}):
			frappe.throw("Registration number must be unique")

	def validate_year(self):
		current_year = datetime.now().year

		if not self.year_of_manufacture:
			frappe.throw("Year of manufacture is required")

		if self.year_of_manufacture < 1950:
			frappe.throw("Year cannot be less than 1950")

		if self.year_of_manufacture > current_year:
			frappe.throw(f"Year cannot be greater than {current_year}")

	def validate_numbers(self):
		if self.odometerkm and self.odometerkm < 0:
			frappe.throw("Odometer cannot be negative")
		if self.acquisition_cost and self.acquisition_cost < 0:
			frappe.throw("Acquisition cost cannot be negative")
		if self.refurbishment_cost and self.refurbishment_cost < 0:
			frappe.throw("Refurbishment cost cannot be negative")

	def calculate_total_investment(self):
		self.total_investment = (self.acquisition_cost or 0) + (self.refurbishment_cost or 0)

	def validate_prices(self):
		if self.expected_selling_price and self.minimum_price:
			if self.minimum_price > self.expected_selling_price:
				frappe.throw("Minimum price cannot exceed expected selling price")


	def check_profit_margin(self):
		settings = frappe.get_single("Dealership Settings")

		if self.expected_selling_price and self.acquisition_cost:
			profit = self.expected_selling_price - self.acquisition_cost
			profit_percent = (profit / self.acquisition_cost) * 100

			if profit_percent < settings.min_profit_margin:
				frappe.throw(
					f"Profit margin {profit_percent:.2f}% is below minimum required {settings.min_profit_margin}%"
				)
	def validate_leaf_category(self):
		if self.vehicle_classification:
			classification_doc = frappe.get_doc("Vehicle Classification", self.vehicle_classification)
			
			if classification_doc.is_group:
				frappe.throw("Please select a leaf-level Vehicle Classification")


	def set_condition_auto(self):
		# Only auto-set if not manually set
		if not self.condition_rating and self.odometerkm:
			if self.odometerkm < 5000:
				self.condition_rating = "Excellent"
			elif self.odometerkm < 20000:
				self.condition_rating = "Good"
			elif self.odometerkm < 50000:
				self.condition_rating = "Fair"
			else:
				self.condition_rating = "Poor"


	def on_trash(self):
		# Prevent deletion if linked in sales
		if frappe.db.exists("Sales Transaction", {"vehicle": self.name}):
			frappe.throw("Cannot delete vehicle. It is linked with a Sales Transaction.")



def notify_customers(vehicle):

	doc = frappe.get_doc("Vehicle Inventory", vehicle)

	# Get customers within budget
	customers = frappe.get_all(
		"Customer Registry",
		fields=["name", "email_address"],
		filters={
			"min_budget": ["<=", doc.expected_selling_price],
			"max_budget": [">=", doc.expected_selling_price]
		}
	)

	for cust in customers:
		if not cust.min_budget or not cust.max_budget:
			continue

		if not (cust.min_budget <= doc.expected_selling_price <= cust.max_budget):
			continue
		if cust.email_address:
			frappe.sendmail(
				recipients=["dhanaalakshminarayanan@gmail.com"],
				subject="New Vehicle Available",
				message=f"""
Hello,

A new vehicle {doc.manufacturer} {doc.model} is available within your budget.

Price: {doc.expected_selling_price}
Type: {doc.vehicle_classification}

Visit showroom for more details.

Thank you.
"""
			)