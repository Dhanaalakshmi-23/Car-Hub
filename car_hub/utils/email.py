import frappe

def send_test_mail():
    print("Function triggered") 

    frappe.sendmail(
        recipients=["dhanaalakshminarayanan@gmail.com", "chethank1407@gmail.com"],
        subject="Test Email",
        message="This is a test email",
        now=True
    )

    print("Email send function called")

def send_email(recipients, subject, message):
    frappe.sendmail(
        recipients=["dhanaalakshminarayanan@gmail.com"],
        subject=subject,
        message=message,
        now=True
    )

def send_system_notification(users, message):
    for user in users:
        frappe.publish_realtime(
            event="msgprint",
            message=message,
            user=user
        )