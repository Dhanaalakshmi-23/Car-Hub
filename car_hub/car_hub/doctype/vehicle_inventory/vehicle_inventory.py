# Copyright (c) 2026, Dhanaa Lakshmi and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime


class VehicleInventory(Document):

	def validate(self):
		self.validate_registration()
		self.validate_year()
		self.calculate_total_investment()
		self.validate_prices()
		self.check_profit_margin()
		self.set_condition_auto()

	def after_insert(self):
		frappe.enqueue(
			"car_hub.car_hub.doctype.vehicle_inventory.vehicle_inventory.notify_customers",
			vehicle=self.name
		)


	def validate_registration(self):
		if frappe.db.exists("Vehicle Inventory", {
			"registration_number": self.registration_number,
			"name": ["!=", self.name]
		}):
			frappe.throw("Registration number must be unique")

	def validate_year(self):
		current_year = datetime.now().year

		if not self.year:
			frappe.throw("Year of manufacture is required")

		if self.year < 1950:
			frappe.throw("Year cannot be less than 1950")

		if self.year > current_year:
			frappe.throw(f"Year cannot be greater than {current_year}")

	def calculate_total_investment(self):
		self.total_investment = (self.acquisition_cost or 0) + (self.refurbishment_cost or 0)

	def validate_prices(self):
		if self.expected_price and self.min_price:
			if self.min_price > self.expected_price:
				frappe.throw("Minimum price cannot exceed expected selling price")
	

	def check_profit_margin(self):
		settings = frappe.get_single("Dealership Settings")

		if self.expected_price and self.acquisition_cost:
			profit = self.expected_price - self.acquisition_cost
			profit_percent = (profit / self.acquisition_cost) * 100

			if profit_percent < settings.min_profit_margin:
				frappe.throw(
					f"Profit margin {profit_percent:.2f}% is below minimum required {settings.min_profit_margin}%"
				)				
				
	def set_condition_auto(self):
		if self.odometerkm:
			if self.odometerkm < 5000:
				self.condition_rating = "Excellent"
			elif self.odometerkm < 20000:
				self.condition_rating = "Good"
			elif self.odometerkm < 50000:
				self.condition_rating = "Fair"
			else:
				self.condition_rating = "Poor"

def notify_customers(vehicle):
	vehicle_doc = frappe.get_doc("Vehicle Inventory", vehicle)

	customers = frappe.get_all(
		"Customer Registry",
		fields=["name", "email_address", "min_budget", "max_budget"]
	)

	for cust in customers:
		if cust.email_address:
			frappe.sendmail(
				recipients=cust.email_address,
				subject="New Vehicle Available",
				message=f"A new vehicle {vehicle_doc.model} is available."
			)