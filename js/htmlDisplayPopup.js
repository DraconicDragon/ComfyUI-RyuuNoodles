import { app } from "../../scripts/app.js";
import { windowManager } from "./ryuuPopupWindowManager.js";

app.registerExtension({
    name: "RyuuNoodles.HTMLDisplayPopup",
    async beforeRegisterNodeDef(nodeType, nodeData) {
        if (nodeData.name !== "Ryuu_HTMLDisplayNode") return;

        nodeType.prototype.onNodeCreated = function () {
            this.addWidget("button", "Show HTML Popup", null, () => {
                const htmlInput = this.widgets.find(w => w.name === "html_string");
                const urlInput = this.widgets.find(w => w.name === "url_opt");
                const useUrlInput = this.widgets.find(w => w.name === "use_url");

                if (!htmlInput) return;

                // Get node title and ID
                const nodeTitle = this.title || this.type || "Unknown Title";
                const nodeId = this.id || "Unknown ID";
                const popupTitle = `${nodeTitle} (ID: ${nodeId})`;

                // Get popup for this specific node
                // Yes, I still call them popups even though they are windows, I think
                const popup = windowManager.getPopupForNode(nodeId.toString());

                const useUrl = useUrlInput ? useUrlInput.value : false;
                const url = urlInput && urlInput.value ? urlInput.value.trim() : "";

                if (useUrl && url) {
                    // Show webpage in popup
                    popup.showUrl(url, popupTitle);
                } else {
                    // Show content from text input
                    const htmlContent = htmlInput.value || "<b>No content provided</b>";
                    popup.show(htmlContent, popupTitle);
                }
            });
        };
    }
});