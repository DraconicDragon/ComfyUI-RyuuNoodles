import { app } from "../../scripts/app.js";
import { htmlPopup } from "./ryuu_popup.js";

app.registerExtension({
    name: "RyuuNoodles.HTMLDisplayNode",
    async beforeRegisterNodeDef(nodeType, nodeData) {
        if (nodeData.name !== "Ryuu_HTMLDisplayNode") return;

        // overriding onNodeCreated to add the render button
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

                // Check if we should use URL or HTML content
                const useUrl = useUrlInput ? useUrlInput.value : false;
                const url = urlInput && urlInput.value ? urlInput.value.trim() : "";

                if (useUrl && url) {
                    // Show webpage in popup
                    htmlPopup.showUrl(url, popupTitle, this);
                } else {
                    // Show HTML content
                    const htmlContent = htmlInput.value || "<b>No content provided</b>";
                    htmlPopup.show(htmlContent, popupTitle, this);
                }
            });
        };
    }
});