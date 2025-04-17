import { api } from "../../scripts/api.js";
import { app } from "../../scripts/app.js";

app.registerExtension({
    name: "RyuuNoodles.TokenCountTextBox",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "Ryuu_TokenCountTextBox") {
            // Store the original onConfigure method
            const onConfigure = nodeType.prototype.onConfigure;

            nodeType.prototype.onNodeCreated = function () {
                onConfigure?.apply(this, arguments);
                // Button used like a label
                let charCountWidget = {
                    type: "button",
                    name: "Token Count: 0 | Character count: 0",
                    callback: () => {
                        alert(
                            "u stinky stop pressing this buttonggg idk how to not make it a button"
                        );
                    },
                };
                this.widgets.splice(0, 0, charCountWidget); // Insert at the top of the widget list

                // Poll for changes to input_text
                let lastText = "";
                // make the interval callback async so we can await the fetch…
                setInterval(async () => {
                    const inputText =
                        this.widgets.find((w) => w.name === "input_text")?.value || "";
                    if (inputText === lastText) return; // stop early if no change to not waste time on api call
                    lastText = inputText;

                    const response = await api.fetchApi("/ryuu/update_token_count", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ text: inputText }),
                    });

                    if (response.status !== 200) {
                        console.error(
                            "Token count API error:",
                            response.status,
                            response.statusText
                        );
                        //return;
                    }

                    // parse the JSON body
                    const data = await response.json();
                    const tokenCount = data.token_count || 0;
                    charCountWidget.name = `Token Count: ${tokenCount} | Character count: ${inputText.length}`;
                    this.setDirtyCanvas(true);
                }, 1000); // Check every Xms, 0 clue if good approach or not but it works
                // check https://docs.comfy.org/custom-nodes/javascript_examples#capture-ui-events for better approach?
            };
        }
    },
});
