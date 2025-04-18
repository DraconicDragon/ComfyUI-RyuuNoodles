import { api } from "../../scripts/api.js";
import { app } from "../../scripts/app.js";

// todo: can probably change to not require reload
const rawSettingsString = (app.extensionManager.setting.get("RyuuNoodles.TokenCountOverlay") || "");
// strip all whitespace
const clean = rawSettingsString.replace(/(?<=\.[^:;]+)\s+/g, "");
const nodeWidgetMapping = {};

clean.split(";")
    .filter(Boolean)
    .forEach(entry => {
        const [nodeWidget, tokList] = entry.split(":");
        if (!nodeWidget || !tokList) return;
        const [nodeName, widgetName] = nodeWidget.split(".");
        if (!nodeName || !widgetName) return;

        nodeWidgetMapping[nodeName] = {
            widget: widgetName,
            tok_types: tokList
                .split(",")
                .map(t => t.toLowerCase())
                .filter(Boolean)
        };
    });

// helper to turn e.g. "clip_l" → "Clip L", "t5_fast" → "T5🚀"
function prettifyTokenizerName(tok) {
    const parts = tok.split("_");
    const hasFast = parts.includes("fast");
    const filtered = parts.filter(p => p !== "fast");
    const title = filtered
        .map(p => p.charAt(0).toUpperCase() + p.slice(1).toLowerCase())
        .join(" ");
    return hasFast ? `${title}🚀` : title;
}

/**
 * Function to start counting tokens in the specified node's widget
 * @param  node - The node object
 * @param {String} widgetField - The name of the widget (usually input name defined in python) to monitor for text changes
 */
function startCounting(node, widgetField, tokTypes) {
    node._lastText = "";
    node._tokenCounts = {}; // will become { clip_l: 42, t5_fast: 56, … }

    setInterval(async () => {
        const w = node.widgets.find(w => w.name === widgetField);
        const inputText = (w?.value ?? "") + ""; // fallback to empty string, ensure it's a string

        if (inputText === node._lastText) return;
        node._lastText = inputText;

        try {
            const resp = await api.fetchApi("/ryuu/update_token_count", { // todo: update endpoint to /ryuu/token_counter/update?
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    text: inputText,
                    tok_types: tokTypes,
                }),
            });
            const data = await resp.json();
            // spit out tokTypes as string
            // console.log(`{tokTypes: ${tokTypes.join(", ")}}`);
            // console.log(JSON.stringify(data));

            node._tokenCounts = data.token_counts || {};
        } catch (e) {
            console.error("Token count API error:", e);
        }

        node.setDirtyCanvas(true); // mark as dirty so redraw happens
    }, 1000); // in milliseconds
}


async function registerTokenCountNode(nodeType, nodeData) {
    const nodeWidgetMappingConfig = nodeWidgetMapping[nodeData.name];
    if (!nodeWidgetMappingConfig) return;

    // preserve original onDrawForeground
    const originalOnDrawFG = nodeType.prototype.onDrawForeground;
    nodeType.prototype.onDrawForeground = function (ctx) {
        originalOnDrawFG?.apply(this, arguments); // call original method, then custom stuff

        // find widget & its actual y‑pos (set by LiteGraph)
        const widget = this.widgets.find(w => w.name === nodeWidgetMappingConfig.widget);
        if (!widget || widget.last_y == null) return;

        // build “Clip L Tokens: 0 | T5🚀 Tokens: 0 | Chars: 0”
        const parts = nodeWidgetMappingConfig.tok_types.map(tt => {
            const cnt = this._tokenCounts[tt] || 0;
            return `${prettifyTokenizerName(tt)} Tokens: ${cnt}`;
        });
        parts.push(`Chars: ${this._lastText.length}`);
        const txt = parts.join(" | ");

        // text styling
        ctx.font = "12px Arial";
        ctx.textAlign = "left";
        ctx.textBaseline = "bottom";

        const x = 10;                 // Left padding
        const y = widget.last_y + 8;  // Just above the widget
        ctx.fillText(txt, x, y);      // draw the text onto node canvas
    };

    // preserve & patch onNodeCreated
    const originalOnNodeCreated = nodeType.prototype.onNodeCreated;
    nodeType.prototype.onNodeCreated = function () {
        originalOnNodeCreated?.apply(this, arguments); // call original method, then custom stuff
        startCounting(this, nodeWidgetMappingConfig.widget, nodeWidgetMappingConfig.tok_types);
    };
}

// Register
app.registerExtension({
    name: "RyuuNoodles.TokenCountOverlay",
    async beforeRegisterNodeDef(nodeType, nodeData) {
        await registerTokenCountNode(nodeType, nodeData);
    },
});
