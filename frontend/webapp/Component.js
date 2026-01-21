sap.ui.define(
  ["sap/ui/core/UIComponent"],
  function (UIComponent) {
    "use strict";

    return UIComponent.extend("attendance.bot.Component", {
      metadata: { manifest: "json" },

      init: function () {
        UIComponent.prototype.init.apply(this, arguments);

        // Load empty model for table binding
        const oModel = new sap.ui.model.json.JSONModel({
          columns: [],
          rows: []
        });

        this.setModel(oModel, "BotModel");
      }
    });
  }
);
