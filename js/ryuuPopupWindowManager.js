import { HTMLPopup } from './ryuuPopup.js';


// Window Manager to handle multiple popups
class PopupWindowManager {
    constructor() {
        this.popups = new Map(); // nodeId -> HTMLPopup
        this.zIndexCounter = 10000;
        this.activePopup = null;
    }

    // Create or get popup for a specific node
    getPopupForNode(nodeId) {
        if (!this.popups.has(nodeId)) {
            const popup = new HTMLPopup(nodeId, this);
            this.popups.set(nodeId, popup);
        }
        return this.popups.get(nodeId);
    }

    // Remove popup for a specific node
    removePopupForNode(nodeId) {
        const popup = this.popups.get(nodeId);
        if (popup) {
            popup.destroy();
            this.popups.delete(nodeId);
            if (this.activePopup === popup) {
                this.activePopup = null;
            }
        }
    }

    // Set active popup (brings to front)
    setActivePopup(popup) {
        if (this.activePopup === popup) return;

        // Unfocus previous active popup
        if (this.activePopup) {
            this.activePopup.setFocused(false);
        }

        // Focus new popup
        this.activePopup = popup;
        popup.setFocused(true);
        popup.bringToFront(++this.zIndexCounter);
    }

    // Check if node still exists in the graph
    cleanupOrphanedPopups() {
        if (!window.app || !app.graph) return;

        const existingNodeIds = new Set();
        if (app.graph._nodes) {
            for (const node of Object.values(app.graph._nodes)) {
                if (node && node.id !== undefined) {
                    existingNodeIds.add(node.id.toString());
                }
            }
        }

        // Remove popups for deleted nodes
        for (const [nodeId, popup] of this.popups.entries()) {
            if (!existingNodeIds.has(nodeId)) {
                console.log(`Removing orphaned popup for deleted node ${nodeId}`);
                this.removePopupForNode(nodeId);
            }
        }
    }
}

// Create the window manager instance
const windowManager = new PopupWindowManager();

// Cleanup orphaned popups periodically
setInterval(() => {
    windowManager.cleanupOrphanedPopups();
}, 2000);

export { windowManager };

