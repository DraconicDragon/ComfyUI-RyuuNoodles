// original code from https://github.com/pythongosssss/ComfyUI-Custom-Scripts/blob/main/web/js/mathExpression.js - modified here

import { app } from "../../scripts/app.js";
import { ComfyWidgets } from "../../scripts/widgets.js";

app.registerExtension({
    name: "RyuuNoodles.LatentSizePicker.NumberDisplay",
    init() {
        const STRING = ComfyWidgets.STRING;
        ComfyWidgets.STRING = function (node, inputName, inputData) {
            const r = STRING.apply(this, arguments);
            r.widget.dynamicPrompts = inputData?.[1].dynamicPrompts;
            return r;
        };
    },
    beforeRegisterNodeDef(nodeType) {
        if (nodeType.comfyClass === "Ryuu_ScaleToMultipleLatentSizePicker") {
            const onDrawForeground = nodeType.prototype.onDrawForeground;


            nodeType.prototype.onDrawForeground = function (ctx) {
                const r = onDrawForeground?.apply?.(this, arguments);

                const v = app.nodeOutputs?.[this.id + ""];
                if (!this.flags.collapsed && v && v.value && Array.isArray(v.value)) {
                    ctx.save();
                    ctx.font = "bold 12px sans-serif";
                    ctx.fillStyle = "dodgerblue";

                    // Display width (value[0]) next to second output (index 1)
                    if (v.value[0] !== undefined && this.outputs && this.outputs[1]) {
                        const widthText = v.value[0] + "";
                        const outputName = this.outputs[1].name || "width";
                        const outputNameWidth = ctx.measureText(outputName).width;
                        const widthSz = ctx.measureText(widthText);
                        const y1 = LiteGraph.NODE_SLOT_HEIGHT * 1.5 + 9;
                        const x1 = this.size[0] - widthSz.width - outputNameWidth - 20; // 20px padding
                        ctx.fillText(widthText, x1, y1);
                    }

                    // Display height (value[1]) next to third output (index 2)
                    if (v.value[1] !== undefined && this.outputs && this.outputs[2]) {
                        const heightText = v.value[1] + "";
                        const outputName = this.outputs[2].name || "height";
                        const outputNameWidth = ctx.measureText(outputName).width;
                        const heightSz = ctx.measureText(heightText);
                        const y2 = LiteGraph.NODE_SLOT_HEIGHT * 2.5 + 9;
                        const x2 = this.size[0] - heightSz.width - outputNameWidth - 20; // 20px padding
                        ctx.fillText(heightText, x2, y2);
                    }
                    ctx.restore();
                }
                return r;
            };
        }
    },
});