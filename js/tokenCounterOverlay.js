import { api } from "../../scripts/api.js";
import { app } from "../../scripts/app.js";

/**
 * Mapping of node types → which widget name holds the text
 * @ex "nodeData.name": "widget_name"  @ex "Ryuu_TokenCountTextBox": "input_text"
 */
const nodeWidgetMapping = {
    "Ryuu_TokenCountTextBox": "input_text", // todo: should probably be a button for this node specifically; btn press -> change tokenizer type 
};

/**
 * Function to start counting tokens in the specified node's widget
 * @param  node - The node object
 * @param {String} widgetField - The name of the widget (usually input name defined in python) to monitor for text changes
 */
function startCounting(node, widgetField) {
    node._lastText = "";
    node._tokenCount = 0;

    // not really efficient but idk how to capture typing ui event 
    // but tokenizer are usually sub 1 second anyway and this doesnt block the UI
    setInterval(async () => {
        const w = node.widgets.find(w => w.name === widgetField);
        const inputText = (w?.value ?? "") + ""; // fallback to empty string, ensure it's a string

        // skip if text didnt change
        if (inputText === node._lastText) return;
        node._lastText = inputText;

        try {
            const resp = await api.fetchApi("/ryuu/update_token_count", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ text: inputText }),
            });
            const data = await resp.json();
            node._tokenCount = data.token_count || 0; // fallback to 0

        } catch (e) {
            console.error("Token count API error:", e);
        }

        node.setDirtyCanvas(true); // mark as dirty so redraw happens
    }, 1000); // in milliseconds
}

async function registerTokenCountNode(nodeType, nodeData) {
    const widgetField = nodeWidgetMapping[nodeData.name];
    if (!widgetField) return;

    // preserve original drawForeground
    const originalOnDrawFG = nodeType.prototype.onDrawForeground;
    nodeType.prototype.onDrawForeground = function (ctx) {
        originalOnDrawFG?.apply(this, arguments); // call original method, then custom stuff

        const widget = this.widgets.find(w => w.name === widgetField);
        if (!widget || widget.last_y == null) return;

        const txt = `Tokens: ${this._tokenCount} | Chars: ${this._lastText.length}`;

        // text styling
        ctx.font = "12px Arial";
        ctx.textAlign = "left";
        ctx.textBaseline = "bottom";

        const x = 10;                 // Left padding
        const y = widget.last_y + 8; // Just above the widget
        ctx.fillText(txt, x, y);      // draw the text onto node canvas
    };

    // preserve & patch onNodeCreated
    const originalOnNodeCreated = nodeType.prototype.onNodeCreated;
    nodeType.prototype.onNodeCreated = function () {
        originalOnNodeCreated?.apply(this, arguments); // call original method, then custom stuff
        startCounting(this, widgetField);
    };
}

// Register
app.registerExtension({
    name: "RyuuNoodles.TokenCountOverlay",
    async beforeRegisterNodeDef(nodeType, nodeData) {
        await registerTokenCountNode(nodeType, nodeData);
    },
});
