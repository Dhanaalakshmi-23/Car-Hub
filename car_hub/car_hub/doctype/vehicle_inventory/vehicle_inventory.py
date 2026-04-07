# Copyright (c) 2026, Dhanaa Lakshmi and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime
from car_hub.utils.notifications import notify_matching_customers


class VehicleInventory(Document):

	def validate(self):
		self.validate_registration()
		self.calculate_total_investment()
		self.validate_prices()
		self.check_profit_margin()
		self.validate_leaf_category()
		self.set_condition_auto()

	def after_insert(self):
		notify_matching_customers(self.name)

	def validate_registration(self):
		if frappe.db.exists("Vehicle Inventory", {
			"registration_number": self.registration_number,
			"name": ["!=", self.name]
		}):
			frappe.throw("Registration number must be unique")


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

			if profit_percent < settings.minimum_profit_margin:
				frappe.throw(
					f"Profit margin {profit_percent:.2f}% is below minimum required {settings.minimum_profit_margin}%"
				)
	def validate_leaf_category(self):
		if self.vehicle_classification:
			classification_doc = frappe.get_doc("Vehicle Classification", self.vehicle_classification)
			
			if classification_doc.is_group:
				frappe.throw("Please select a leaf-level Vehicle Classification")


	def set_condition_auto(self):
		# Only auto-set if not manually set
		if not self.condition_rating and self.odometer_reading:
			if self.odometer_reading < 5000:
				self.condition_rating = "Excellent"
			elif self.odometer_reading < 20000:
				self.condition_rating = "Good"
			elif self.odometer_reading < 50000:
				self.condition_rating = "Fair"
			else:
				self.condition_rating = "Poor"


	def on_trash(self):
		# Prevent deletion if linked in sales
		if frappe.db.exists("Sales Transaction", {"vehicle": self.name}):
			frappe.throw("Cannot delete vehicle. It is linked with a Sales Transaction.")


