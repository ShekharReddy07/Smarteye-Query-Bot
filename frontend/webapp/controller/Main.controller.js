sap.ui.define([
    "sap/ui/core/mvc/Controller",
    "sap/ui/model/json/JSONModel",
    "sap/m/MessageToast"
], function (Controller, JSONModel, MessageToast) {
    "use strict";

    return Controller.extend("attendance.bot.controller.Main", {

        onInit: function () {
            const oModel = new JSONModel({
                question: "",
                messages: [
                    { role: "bot", text: "👋 Hi! Ask me any attendance query." }
                ]
            });

            const oResultsModel = new JSONModel({
                columns: [],
                rows: []
            });

            this.getView().setModel(oModel);
            this.getView().setModel(oResultsModel, "results");
        },

        // ---------------------------
        // ASK — CALL BACKEND API
        // ---------------------------
        onAsk: function () {
            const oModel = this.getView().getModel();
            const oResults = this.getView().getModel("results");

            const question = oModel.getProperty("/question");

            if (!question) {
                MessageToast.show("Please type a question.");
                return;
            }

            // Add user message in chat
            const msgs = oModel.getProperty("/messages");
            msgs.push({ role: "user", text: question });
            oModel.setProperty("/messages", msgs);

            // Backend URL
            const BACKEND_URL = "http://127.0.0.1:8000/ask";

            fetch(BACKEND_URL, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ question: question })
            })
                .then(res => res.json())
                .then(data => {

                    if (data.status !== "ok") {
                        MessageToast.show("Backend error: " + data.message);
                        return;
                    }

                    // Fill table data
                    oResults.setProperty("/columns", data.columns);
                    oResults.setProperty("/rows", data.rows);

                    this.buildTable(data.columns);

                    // Add bot reply
                    msgs.push({
                        role: "bot",
                        text: "Fetched " + data.rows.length + " rows."
                    });
                    oModel.setProperty("/messages", msgs);
                })
                .catch(err => {
                    console.error(err);
                    MessageToast.show("Failed to connect backend.");
                });
        },

        // ---------------------------
        // CLEAR CHAT + TABLE
        // ---------------------------
        onClear: function () {
            const oModel = this.getView().getModel();
            const oResults = this.getView().getModel("results");

            oModel.setProperty("/question", "");
            oModel.setProperty("/messages", [
                { role: "bot", text: "👋 Hi! Ask me any attendance query." }
            ]);

            oResults.setProperty("/columns", []);
            oResults.setProperty("/rows", []);

            this.buildTable([]);
        },

        // ---------------------------
        // ⚡ TEST SAMPLE DATA
        // ---------------------------
        onTestSample: function () {

            const oSample = {
                columns: ["ECode", "EName", "Dept_Code", "WDate", "Work_HR"],
                rows: [
                    { ECode: "NZ1073", EName: "Pradip Mallick", Dept_Code: "25", WDate: "2025-01-01", Work_HR: 8 },
                    { ECode: "NZ1056", EName: "Kishor Ram", Dept_Code: "25", WDate: "2025-01-01", Work_HR: 7 },
                    { ECode: "NZ1081", EName: "Upendra Rout", Dept_Code: "25", WDate: "2025-01-01", Work_HR: 6 }
                ]
            };

            const oResults = this.getView().getModel("results");

            oResults.setProperty("/columns", oSample.columns);
            oResults.setProperty("/rows", oSample.rows);

            this.buildTable(oSample.columns);

            MessageToast.show("Sample data loaded!");
        },

        // ---------------------------
        // BUILD TABLE (DYNAMIC)
        // ---------------------------
        buildTable: function (columns) {
            const oTable = this.byId("resultsTable");
        
            // Columns we actually want to show
            const allowedColumns = [
                "ECode",
                "EName",
                "Dept_Code",
                "WDate",
                "Work_HR",
                "Work_Type",
                "Grade",

            ];
        
            // Clear old columns
            oTable.removeAllColumns();
        
            // Create only meaningful columns
            allowedColumns.forEach(col => {
                if (columns.includes(col)) {
                    oTable.addColumn(
                        new sap.ui.table.Column({
                            label: new sap.m.Label({ text: col }),
                            template: new sap.m.Text({
                                text: "{results>" + col + "}"
                            }),
                            width: "140px"
                        })
                    );
                }
            });
        
            oTable.setVisible(true);
        }
        

    });
});
