import { api } from "../../scripts/api.js";
import { app } from "../../scripts/app.js";

app.registerExtension({
    name: "RyuuNoodles.Settings",
    settings: [
        // NOTE: The order the settings are displayed in the UI is reverse from how they show up in code, except for category name, thats alphabetical it seems 
        // region: TCO settings
        /// Token Counter Overlay settings
        {
            id: "RyuuSettings.TokenizerAddSpecialTokens",
            category: ['RyuuNoodles 🐲', 'Token Count Overlay', 'Tokenizer special tokens'],
            name: "Include special tokens",
            type: "boolean",
            defaultValue: false,
            tooltip: "This will add the number of special tokens per tokenizer to the token count.\n" +
                "E.g: If enabled, CLIP-L will always show 2 tokens more because of 'startoftext' and 'endoftext' tokens " +
                "which are invisible to the user.",
            onChange: (newVal, oldVal) => {
                console.log(`RyuuSettings.TokenizerAddSpecialTokens has been changed from ${oldVal} to ${newVal}`);
            },
        },

        {
            id: "RyuuSettings.TokenCountOverlay.SupportBreakKeyword",
            category: ['RyuuNoodles 🐲', 'Token Count Overlay', 'Support "BREAK" for CLIP-L'],
            name: "Support 'BREAK' keyword",
            type: "boolean",
            defaultValue: false,
            tooltip: "This will simply increase the CLIP-L counter number to fill up to the next upper multiple of 75 " +
                "when 'BREAK' is encountered in the text. NOTE: ComfyUI by default doesn't support 'BREAK' " +
                "and you need to use a custom node for the actual functionality.",
            onChange: (newVal, oldVal) => {
                console.log(`RyuuSettings.TokenCountOverlay.SupportBreakKeyword has been changed from ${oldVal} to ${newVal}`);
            },
        },

        {
            id: "RyuuSettings.TokenCountOverlay.CompactMode",
            category: ['RyuuNoodles 🐲', 'Token Count Overlay', 'Compact Mode'],
            name: "Compact Mode",
            type: "boolean",
            defaultValue: false,
            tooltip: "This will simply remove the word 'Tokens' from the token count overlay to save space.\n" +
                "Also changes the name of some tokenizers to be shorter, e.g. 'GEMMA2' → 'G2', 'LLAMA3' → 'L3'.",
            onChange: (newVal, oldVal) => {
                console.log(`RyuuSettings.TokenCountOverlay.ExcludeTokensWord has been changed from ${oldVal} to ${newVal}`);
            },
        },

        {
            id: "RyuuSettings.TokenCountOverlay.UpdateInterval",
            category: ['RyuuNoodles 🐲', 'Token Count Overlay', 'Update Interval'],
            name: "Update Interval in ms",
            type: "slider",
            attrs: {
                min: 100,
                max: 2500,
                step: 25,
            },
            defaultValue: 1000,
            tooltip: "Default: 1000\nSuggested to stay above 200ms.",
            onChange: (newVal, oldVal) => {
                console.log(`RyuuSettings.TokenizerAddSpecialTokens.UpdateInterval has been changed from ${oldVal} to ${newVal}`);
            },
        },

        {
            id: "RyuuSettings.TokenCountOverlay", // don't change, use category for name setting
            // ["Category name", "Section heading", "Setting label"], but "Settings label" seems to be overwritten by 'name:'
            category: ['RyuuNoodles 🐲', 'Token Count Overlay', 'Nodes'],
            name: "Nodes configuration",
            type: "text",
            defaultValue: "Ryuu_TokenCountTextBox.input_text:CLIP_L,T5_FAST;CLIPTextEncode.text:CLIP_L,T5_FAST;",
            tooltip: "Enter the node names (internal `nodeData.name`), their widget names and tokenizer types. " +
                "A token counter will appear above the supplied widget.\n" +
                "Supported tokenizer types: CLIP_L, T5, T5_FAST, UMT5, GEMMA2, GEMMA3, LLAMA3, QWEN25VL, AURAFLOW\n" +
                "Please check the GitHub README for more info",
            // todo: tooltips and textbox are far too small for this :pensive:
        },

        {
            id: "RyuuSettings.TokenCountOverlay.Enabled",
            category: ['RyuuNoodles 🐲', 'Token Count Overlay', 'Enable/Disable'],
            name: "Enable Token Counter Overlay",
            type: "boolean",
            defaultValue: true,
            onChange: (newVal, oldVal) => {
                console.log(`RyuuSettings.TokenCountOverlay.Enabled changed from ${oldVal} to ${newVal}`);
                // Notify all nodes to update their overlays immediately
                window.dispatchEvent(new CustomEvent("RyuuNoodles.TokenCounterOverlay.Toggle", { detail: newVal }));
            },
        },
        // endregion: TCO settings

        // region: General settings
        /// General settings
        {
            id: "RyuuSettings.General.LogLevel",
            category: ['RyuuNoodles 🐲', 'General', 'Log Level'],
            name: "Set Log Level",
            type: "combo",
            defaultValue: "Warning",
            options: ["Debug", "Info", "Warning", "Error", "Critical"],
            tooltip: "Set the log level for RyuuNoodles backend. " +
                "'Warning' is recommended if you don't want to see the generic " +
                "messages from nodes like switches or scale to multiple.",
            onChange: async (newVal, oldVal) => {
                //console.log(`RyuuSettings.General.LogLevel has been changed from ${oldVal} to ${newVal}`);
                try {
                    const response = await api.fetchApi("/ryuu/set_loglevel", {
                        method: "PUT",
                        body: JSON.stringify({ loglevel: newVal }),
                    });
                    const result = await response.json();
                    if (result.status === "success" && result.loglevel === newVal.toUpperCase()) {
                        console.log(`RyuuSettings.General.LogLevel updated successfully to ${result.loglevel}`);
                    } else {
                        console.error("Failed to update RyuuSettings.General.LogLevel:", result);
                    }
                } catch (err) {
                    console.error("Error updating RyuuSettings.General.LogLevel:", err);
                }
            },
        },
        // endregion: General settings
    ],
});

