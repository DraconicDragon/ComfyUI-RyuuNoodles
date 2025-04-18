import { api } from "../../scripts/api.js";
import { app } from "../../scripts/app.js";

app.registerExtension({
    name: "RyuuNoodles.Settings",
    settings: [
        {
            id: "RyuuNoodles.TokenCountOverlay", // don't change, use category for name setting
            // ["Category name", "Section heading", "Setting label"], but "Settings label" seems to be overwritten by 'name:'
            category: ['RyuuNoodles 🐲', 'Token Count Overlay', 'Nodes'],
            name: "Nodes configuration (Reload required on change)",
            type: "text",
            defaultValue: "Ryuu_TokenCountTextBox.input_text:CLIP_L,T5_FAST;",
            tooltip: "Enter the node names (internal nodeData.name), their widget names and tokenizer types. " +
                "A token counter will appear above the supplied widget.\n" +
                "Format: 'Node_Name.widget_name:Tokenizer1,Tok2,Tok3;Node_Name2.widget_name:Tok1;'.\n" +
                "Example: 'Ryuu_TokenCountTextBox.input_text:CLIP_L,T5_FAST;'\n" +
                "Currently accepted tokenizer types: CLIP_L, T5, T5_FAST and LLAMA3.",
            // todo: tooltips and textbox are far too small for this :pensive:

            // onChange: async (newVal) => {
            //     api.fetchApi("/ryuu/token_count_overlay/update", {
            //         method: "POST",
            //         body: JSON.stringify({ apikey: newVal }),
            //     });
            // }
        },
    ],
});

