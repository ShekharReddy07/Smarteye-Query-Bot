sap.ui.define([
  "sap/ui/model/json/JSONModel"
], function(JSONModel) {
"use strict";
return {
  createAppModel: function () {
    return new JSONModel({
      question: "",
      messages: [
        { role: "bot", text: "👋 Hi! Ask me any attendance query." }
      ],
      results: { columns: [], rows: [] }
    });
  }
};
});