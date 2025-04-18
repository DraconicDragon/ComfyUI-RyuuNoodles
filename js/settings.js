import { app } from "../../scripts/app.js";

app.registerExtension({
    name: "RyuuNoodles.Settings",
    settings: [
        {
            id: "RyuuSettings.TokenCountOverlay", // don't change, use category for name setting
            // ["Category name", "Section heading", "Setting label"], but "Settings label" seems to be overwritten by 'name:'
            category: ['RyuuNoodles 🐲', 'Token Count Overlay', 'Nodes'],
            name: "Nodes configuration (Reload required on change)",
            type: "text",
            defaultValue: "Ryuu_TokenCountTextBox.input_text:CLIP_L,T5_FAST;CLIPTextEncode.text:CLIP_L,T5_FAST;",
            tooltip: "Enter the node names (internal nodeData.name), their widget names and tokenizer types. " +
                "A token counter will appear above the supplied widget.\n" +
                //"Format: 'Node_Name.widget_name:Tokenizer1,Tok2,Tok3;Node_Name2.widget_name:Tok1;'.\n" +
                //"Example: 'Ryuu_TokenCountTextBox.input_text:CLIP_L,T5_FAST;'\n" +
                "Supported tokenizer types: CLIP_L, T5, T5_FAST, UMT5, GEMMA2, LLAMA3, AURAFLOW\n" +
                "Please check the GitHub README for more info",
            // todo: tooltips and textbox are far too small for this :pensive:
        },

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
    ],
});

