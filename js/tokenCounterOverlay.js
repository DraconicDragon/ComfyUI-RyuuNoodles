import { api } from "../../scripts/api.js";
import { app } from "../../scripts/app.js";

const compactNames = {
    gemma2: "G2",
    gemma3: "G3",
    llama3: "L3",
    qwen25vl: "Q2.5VL",
    auraflow: "AF",
};
// todo: move this to some config file maybe? related todo in pyserver file

function isTokenCounterEnabled() {
    return app.extensionManager.setting.get("RyuuSettings.TokenCountOverlay.Enabled") !== false;
}

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
function prettifyTokenizerName(tok, compactMode) {
    if (compactMode && compactNames[tok.toLowerCase()]) {
        return compactNames[tok.toLowerCase()];
    }
    const parts = tok.split("_");
    const hasFast = parts.includes("fast");
    const filtered = parts.filter(p => p !== "fast");
    const title = filtered
        .map(p => p.charAt(0).toUpperCase() + p.slice(1).toLowerCase())
        .join(" ");
    return hasFast ? `${title}🚀` : title;
}

async function updateTokenCount(node) {
    // Don't do anything if disabled
    if (!isTokenCounterEnabled()) return;

    const rawSettingsString = app.extensionManager.setting.get("RyuuSettings.TokenCountOverlay") || "";
    const addSpecialTokens = app.extensionManager.setting.get("RyuuSettings.TokenizerAddSpecialTokens") || false;
    const SupportBreakKeyword = app.extensionManager.setting.get("RyuuSettings.TokenCountOverlay.SupportBreakKeyword") || false;
    const mapping = parseSettingsString(rawSettingsString);
    const mapConfig = mapping[node._mapConfigName];

    if (!mapConfig) return;

    const widget = node.widgets.find(w => w.name === mapConfig.widget);
    if (!widget) return;

    const inputText = (widget.value ?? "") + "";

    // skip if text unchanged
    if (inputText === node._lastText) return;

    node._lastText = inputText;

    try {
        const resp = await api.fetchApi("/ryuu/update_token_count", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                text: inputText,
                tok_types: mapConfig.tok_types,
                add_special_tokens: addSpecialTokens,
                support_break_keyword: SupportBreakKeyword,
            }),
        });

        const data = await resp.json();
        node._tokenCounts = data.token_counts || {};
    } catch (e) {
        console.error("[RyuuNoodles TokenCounterOverlay] Error:", e);
        node._tokenCounts = {};
    }

    node.setDirtyCanvas?.(true);
}

// Enable token counting
function enableCounting(node) {
    // Clean up first to avoid duplicate handlers
    disableCounting(node);

    // Initialize state
    node._lastText = "";
    node._tokenCounts = {};

    // a special debounce function that reads the interval dynamically
    node._debouncedUpdate = function () {
        // Clear any existing timeout
        if (node._updateTimeout) {
            clearTimeout(node._updateTimeout);
        }

        // Get the current interval from settings
        const updateInterval = app.extensionManager.setting.get("RyuuSettings.TokenCountOverlay.UpdateInterval") || 1000;

        // Schedule the update with the current interval
        node._updateTimeout = setTimeout(() => {
            updateTokenCount(node);
        }, updateInterval);
    };

    // Find the target widget
    const rawSettingsString = app.extensionManager.setting.get("RyuuSettings.TokenCountOverlay") || "";
    const mapping = parseSettingsString(rawSettingsString);
    const mapConfig = mapping[node._mapConfigName];

    if (!mapConfig) return;

    const widget = node.widgets.find(w => w.name === mapConfig.widget);
    if (!widget) return;

    // Save original callback if not already saved
    if (!node._originalWidgetCallback) {
        node._originalWidgetCallback = widget.callback;
    }

    widget.callback = function (...args) {
        // Call original if it exists
        if (node._originalWidgetCallback) {
            node._originalWidgetCallback.apply(this, args);
        }

        // Only call our update if enabled
        if (isTokenCounterEnabled()) {
            node._debouncedUpdate();
        }
    };

    // Force initial update
    updateTokenCount(node);
}

// Disable token counting
function disableCounting(node) {
    // Clear any pending timeout
    if (node._updateTimeout) {
        clearTimeout(node._updateTimeout);
        node._updateTimeout = null;
    }

    // Clear token counts to hide display
    node._tokenCounts = {};

    // Restore original widget callback if there's one
    if (node._originalWidgetCallback) {
        const rawSettingsString = app.extensionManager.setting.get("RyuuSettings.TokenCountOverlay") || "";
        const mapping = parseSettingsString(rawSettingsString);
        const mapConfig = mapping[node._mapConfigName];

        if (mapConfig) {
            const widget = node.widgets.find(w => w.name === mapConfig.widget);
            if (widget) {
                widget.callback = node._originalWidgetCallback;
            }
        }
    }

    // Clean up other properties
    node._debouncedUpdate = null;
    node.setDirtyCanvas?.(true);
}

// Listen for toggle changes
window.addEventListener("RyuuNoodles.TokenCounterOverlay.Toggle", (e) => {
    const enabled = e.detail;

    // Sync the runtime toggle back into the saved setting,
    // so isTokenCounterEnabled() will actually return true again
    app.extensionManager.setting.set(
        "RyuuSettings.TokenCountOverlay.Enabled",
        enabled
    );

    for (const node of Object.values(app.graph._nodes || {})) {
        if (node && node._mapConfigName) {
            if (enabled) {
                enableCounting(node);
            } else {
                disableCounting(node);
            }
        }
    }
});

async function registerTokenCountNode(nodeType, nodeData) {
    // remember node name in each instance
    const theNodeName = nodeData.name;

    // preserve original onDrawForeground
    const originalOnDrawFG = nodeType.prototype.onDrawForeground;
    nodeType.prototype.onDrawForeground = function (ctx) {
        originalOnDrawFG?.apply(this, arguments); // call original method, then custom stuff

        // Only draw overlay if enabled
        if (!isTokenCounterEnabled() || this.collapsed) return;

        // re‑parse settings so widget renames or tok_types changes apply immediately
        const rawSettingsString = app.extensionManager.setting.get("RyuuSettings.TokenCountOverlay") || "";
        const mapping = parseSettingsString(rawSettingsString);
        const nodeWidgetMappingConfig = mapping[theNodeName];
        if (!nodeWidgetMappingConfig) return;

        // find widget & its actual y‑pos (set by LiteGraph)
        const widget = this.widgets.find(w => w.name === nodeWidgetMappingConfig.widget);
        if (!widget || widget.last_y == null) return;

        // build "Clip L Tokens: 0 | T5🚀 Tokens: 0 | Chars: 0"
        const compactMode = app.extensionManager.setting.get("RyuuSettings.TokenCountOverlay.CompactMode") === true;
        const parts = nodeWidgetMappingConfig.tok_types.map(tt => {
            const cnt = this._tokenCounts?.[tt] || 0;
            const tokenLabel = compactMode ? "" : " Tokens";
            return `${prettifyTokenizerName(tt, compactMode)}${tokenLabel}: ${cnt}`;
        });
        parts.push(`${compactMode ? "C" : "Chars"}: ${(this._lastText || "").length}`);
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

        // Only enable counting if the toggle is enabled
        if (isTokenCounterEnabled()) {
            enableCounting(this);
        }
    };

    // Clean up on node removal
    const originalOnRemoved = nodeType.prototype.onRemoved;
    nodeType.prototype.onRemoved = function () {
        disableCounting(this);
        this._originalWidgetCallback = null; // Completely clean up
        originalOnRemoved?.apply(this, arguments);
    };
}

// Register
app.registerExtension({
    name: "RyuuNoodles.TokenCountOverlay",
    async beforeRegisterNodeDef(nodeType, nodeData) {
        await registerTokenCountNode(nodeType, nodeData);
    },
});
