frappe.listview_settings["Vehicle Sale"] = {
    get_indicator: function (doc) {
        if (doc.workflow_state == "Draft") {
            return [__("Draft"), "orange", "workflow_state,=,Draft"];
        }
        if (doc.workflow_state == "Submitted") {
            return [__("Submitted"), "blue", "workflow_state,=,Submitted"];
        }
        if (doc.workflow_state == "Consultant Review") {
            return [__("Consultant Review"), "yellow", "workflow_state,=,Consultant Review"];
        }
        if (doc.workflow_state == "Manager Review") {
            return [__("Manager Review"), "green", "workflow_state,=,Manager Review"];
        }
        if (doc.workflow_state == "Documentation In Progress") {
            return [__("Documentation In Progress"), "purple", "workflow_state,=,Documentation In Progress"];
        }
        if (doc.workflow_state == "Payment Pending") {
            return [__("Payment Pending"), "red", "workflow_state,=,Payment Pending"];
        }
        if (doc.workflow_state == "Payment Received") {
            return [__("Payment Received"), "green", "workflow_state,=,Payment Received"];
        }
        if (doc.workflow_state == "Delivered") {
            return [__("Delivered"), "blue", "workflow_state,=,Delivered"];
        }
        if (doc.workflow_state == "Closed") {
            return [__("Closed"), "gray", "workflow_state,=,Closed"];
        }
        if (doc.workflow_state == "Cancelled") {
            return [__("Cancelled"), "red", "workflow_state,=,Cancelled"];
        }
    }};
