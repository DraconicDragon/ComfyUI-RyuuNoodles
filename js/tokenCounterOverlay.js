import { api } from "../../scripts/api.js";
import { app } from "../../scripts/app.js";

// Parse the raw semicolon‑delimited setting string into a JS map:
// { nodeName: { widget, tok_types: [...] } }
function parseSettingsString(raw) {
    const clean = (raw || "").replace(/(?<=\.[^:;]+)\s+/g, ""); // strip whitespace
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
    return nodeWidgetMapping;
}

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

// Function to start counting tokens in the specified node's widget
function startCounting(node) {
    node._lastText = "";
    node._tokenCounts = {};

    // using a recursive timeout to be able to adjust delay every tick
    async function tick() {
        // read settings dynamically
        const rawSettingsString = app.extensionManager.setting.get("RyuuSettings.TokenCountOverlay") || "";
        const updateInterval = app.extensionManager.setting.get("RyuuSettings.TokenCountOverlay.UpdateInterval") || 1000;ore
        const addSpecialTokens = app.extensionManager.setting.get("RyuuSettings.TokenizerAddSpecialTokens") || false; 
        const mapping = parseSettingsString(rawSettingsString);
        const mapConfig = mapping[node._mapConfigName];
        if (!mapConfig) return;

        // find the widget each tick in case they renamed it
        const w = node.widgets.find(w => w.name === mapConfig.widget);
        const inputText = (w?.value ?? "") + "";

        // skip if unchanged
        if (inputText !== node._lastText) {
            node._lastText = inputText;
            try {
                const resp = await api.fetchApi("/ryuu/update_token_count", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        text: inputText,
                        tok_types: mapConfig.tok_types,
                        add_special_tokens: addSpecialTokens,
                    }),
                });

                const data = await resp.json();
                node._tokenCounts = data.token_counts || {};

            } catch (e) {
                console.error("Token count error:", e);
            }
            node.setDirtyCanvas(true);
        }

        // schedule next tick with a possibly new interval
        setTimeout(tick, updateInterval);
    }

    // start the function off
    tick();
}


async function registerTokenCountNode(nodeType, nodeData) {
    // remember node name in each instance
    const theNodeName = nodeData.name;

    // preserve original onDrawForeground
    const originalOnDrawFG = nodeType.prototype.onDrawForeground;
    nodeType.prototype.onDrawForeground = function (ctx) {
        originalOnDrawFG?.apply(this, arguments); // call original method, then custom stuff

        // re‑parse settings so widget renames or tok_types changes apply immediately
        const rawSettingsString = app.extensionManager.setting.get("RyuuSettings.TokenCountOverlay") || "";
        const mapping = parseSettingsString(rawSettingsString);
        const nodeWidgetMappingConfig = mapping[theNodeName];
        if (!nodeWidgetMappingConfig) return;

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
        this._mapConfigName = theNodeName;
        startCounting(this);
    };
}

// Register
app.registerExtension({
    name: "RyuuNoodles.TokenCountOverlay",
    async beforeRegisterNodeDef(nodeType, nodeData) {
        await registerTokenCountNode(nodeType, nodeData);
    },
});
