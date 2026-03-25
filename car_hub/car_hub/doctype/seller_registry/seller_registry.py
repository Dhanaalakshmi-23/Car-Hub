# Copyright (c) 2026, Dhanaa Lakshmi and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class SellerRegistry(Document):
	def validate(self):
		
		self.validate_id_proof()
	def validate_id_proof(self):
		if self.seller_type == "Individual Owner":
			if not self.id_proof_type and not self.id_proof_number:
				frappe.throw("ID Proof Type and Number are required when Seller Type is Individual Owner")
	