
class HTMLPopup {
    constructor(nodeId, windowManager) {
        this.nodeId = nodeId;
        this.windowManager = windowManager;
        this.focused = true;

        // Create main container
        this.container = document.createElement("div");
        Object.assign(this.container.style, {
            position: "fixed",
            top: "50%",
            left: "50%",
            transform: "translate(-50%, -50%)",
            backgroundColor: "#2a2a2a",
            borderRadius: "8px",
            boxShadow: "0 4px 20px rgba(0, 0, 0, 0.5)",
            zIndex: "10000", // 1000 is below horizontal bar
            minWidth: "200px",
            minHeight: "150px",
            maxWidth: "90vw",
            maxHeight: "90vh",
            display: "flex",
            flexDirection: "column",
            overflow: "hidden",
            fontFamily: "Arial, sans-serif",
            resize: "both",
        });

        // Add click handler to bring popup to front
        this.container.addEventListener('mousedown', () => {
            this.windowManager.setActivePopup(this);
        });

        // Create header (draggable area + collapse + title + close button)
        this.header = document.createElement("div");
        this.updateHeaderStyle(true); // Start focused
        this.container.appendChild(this.header);

        // Collapse button
        this.collapseBtn = document.createElement("button");
        this.collapseBtn.innerHTML = "&#x25B2;";
        Object.assign(this.collapseBtn.style, {
            background: "none",
            border: "none",
            color: "#eee",
            fontSize: "16px",
            cursor: "pointer",
            padding: "0 12px", // Horizontal padding only
            margin: "0", // Remove all margins
            transition: "color 0.2s, background 0.2s",
            borderRadius: "0", // Remove border radius for full coverage
            height: "100%", // Full height of header
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            flexShrink: "0" // Prevent shrinking
        });
        this.collapseBtn.onmouseenter = () => {
            this.collapseBtn.style.color = "#0af";
            this.collapseBtn.style.background = "#222";
        };
        this.collapseBtn.onmouseleave = () => {
            this.collapseBtn.style.color = "#eee";
            this.collapseBtn.style.background = "none";
        };
        this.collapseBtn.onclick = () => this.toggleCollapse();
        this.header.appendChild(this.collapseBtn);

        // Title
        this.title = document.createElement("div");
        this.title.textContent = "HTML Content";
        Object.assign(this.title.style, {
            fontSize: "13px",
            fontWeight: "bold",
            color: "#eee",
            flex: "1",
            padding: "0 8px", // Only horizontal padding
            display: "flex",
            alignItems: "center" // Center text vertically
        });
        this.header.appendChild(this.title);

        // Close button
        this.closeBtn = document.createElement("button");
        this.closeBtn.textContent = "×";
        Object.assign(this.closeBtn.style, {
            background: "none",
            border: "none",
            color: "#fff",
            fontSize: "20px",
            cursor: "pointer",
            padding: "0 12px", // Horizontal padding only
            margin: "0", // Remove all margins
            fontWeight: "bold",
            transition: "color 0.2s, background 0.2s",
            borderRadius: "0", // Remove border radius for full coverage
            height: "100%", // Full height of header
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            flexShrink: "0" // Prevent shrinking
        });
        this.closeBtn.onmouseenter = () => {
            this.closeBtn.style.color = "#fff";
            this.closeBtn.style.background = "#c00";
        };
        this.closeBtn.onmouseleave = () => {
            this.closeBtn.style.color = "#fff";
            this.closeBtn.style.background = "none";
        };
        this.closeBtn.onclick = () => this.windowManager.removePopupForNode(this.nodeId);
        this.header.appendChild(this.closeBtn);

        // Content area
        this.content = document.createElement("div");
        Object.assign(this.content.style, {
            padding: "12px",
            overflowY: "auto",
            color: "#eee",
            flex: "1",
            transition: "max-height 0.2s",
            // Force scrollbars to show
            scrollbarWidth: "thin",
            scrollbarColor: "#666 #333"
        });

        // Add scrollbar styles for webkit browsers
        const style = document.createElement('style');
        style.textContent = `
            .ryuu-popup-content::-webkit-scrollbar {
                width: 8px;
            }
            .ryuu-popup-content::-webkit-scrollbar-track {
                background: #333;
            }
            .ryuu-popup-content::-webkit-scrollbar-thumb {
                background: #666;
                border-radius: 4px;
            }
            .ryuu-popup-content::-webkit-scrollbar-thumb:hover {
                background: #888;
            }
        `;
        document.head.appendChild(style);
        this.content.className = "ryuu-popup-content";

        // Create shadow DOM for CSS isolation
        if (this.content.attachShadow) {
            this.shadowRoot = this.content.attachShadow({ mode: 'closed' });
            this.htmlContainer = document.createElement('div');
            Object.assign(this.htmlContainer.style, {
                color: "#eee",
                fontFamily: "Arial, sans-serif"
            });
            this.shadowRoot.appendChild(this.htmlContainer);
        } else {
            this.htmlContainer = this.content;
        }

        this.container.appendChild(this.content);

        // Make draggable
        this.makeDraggable();

        // Add to document
        document.body.appendChild(this.container);

        // Initially hidden
        this.hide();

        // Collapse state
        this.collapsed = false;
        this._preCollapse = null;

        // Out of bounds state for right/bottom dragging
        this._originalSize = null;
        this._isOOBResizing = false;

        // Track manual resizing when collapsed
        this.resizeObserver = new ResizeObserver(() => {
            // Only update if collapsed, has preCollapse data, AND not currently being resized by OOB logic
            if (this.collapsed && this._preCollapse && !this._isOOBResizing) {
                // Update the saved width if manually resized while collapsed
                const currentWidth = this.container.offsetWidth + "px";
                this._preCollapse.width = currentWidth;

                // Clear _originalSize to prevent it from overriding manual resize
                this._originalSize = null;
            }
        });
        this.resizeObserver.observe(this.container);

        // Prevent pointer events on content during drag/resize
        this.container.addEventListener('mousedown', (e) => {
            const rect = this.container.getBoundingClientRect();
            const isHeaderDrag = e.target.closest('.header') || e.clientY <= rect.top + 32;
            const isResize = e.clientX >= rect.right - 20 && e.clientY >= rect.bottom - 20;

            if (isHeaderDrag || isResize) {
                // Disable pointer events on content during interaction
                this.content.style.pointerEvents = 'none';

                const enablePointerEvents = () => {
                    this.content.style.pointerEvents = 'auto';
                    document.removeEventListener('mouseup', enablePointerEvents);
                };

                document.addEventListener('mouseup', enablePointerEvents);
            }
        });
    }

    // Update header style based on focus state
    updateHeaderStyle(focused) {
        const backgroundColor = focused ? "#333" : "#2a2a2a";
        const borderColor = focused ? "#444" : "#333";

        Object.assign(this.header.style, {
            padding: "0",
            backgroundColor: backgroundColor,
            borderBottom: `1px solid ${borderColor}`,
            display: "flex",
            alignItems: "stretch",
            cursor: "move",
            userSelect: "none",
            height: "32px",
            minHeight: "32px"
        });
    }

    // Set focus state
    setFocused(focused) {
        this.focused = focused;
        this.updateHeaderStyle(focused);
    }

    // Bring popup to front
    bringToFront(zIndex) {
        this.container.style.zIndex = zIndex;
    }

    // Show popup with HTML content
    show(html, title = "HTML Content") {
        this.title.textContent = title;
        // Restore padding for HTML content
        this.content.style.padding = "12px";
        this.htmlContainer.innerHTML = html;

        // Reset htmlContainer styles for HTML content
        Object.assign(this.htmlContainer.style, {
            color: "#eee",
            fontFamily: "Arial, sans-serif",
            width: "auto",
            height: "auto",
            margin: "0",
            padding: "0",
            display: "block",
            boxSizing: "border-box"
        });

        this.container.style.display = "flex";

        // Always center on screen
        this.container.style.top = "50%";
        this.container.style.left = "50%";
        this.container.style.transform = "translate(-50%, -50%)";

        // Set initial size of viewport
        const initialWidth = Math.floor(window.innerWidth * 0.55);
        const initialHeight = Math.floor(window.innerHeight * 0.65);

        this.container.style.width = initialWidth + "px";
        this.container.style.height = initialHeight + "px";

        this.container.style.resize = "both";
        this.collapsed = false;
        this.content.style.display = "block";
        this.collapseBtn.innerHTML = "&#x25B2;";
        this._originalSize = null; // Reset original size

        // Bring to front
        this.windowManager.setActivePopup(this);
        return this;
    }

    // Show popup with URL content using iframe
    showUrl(url, title = "Web Content") {
        this.title.textContent = title;
        // Remove padding from content area when showing iframe
        this.content.style.padding = "0";

        // Convert YouTube URLs to embeddable format
        const embedUrl = this.convertToEmbeddableUrl(url);

        // Create iframe to display the webpage
        const iframe = document.createElement('iframe');
        Object.assign(iframe.style, {
            width: "100%",
            height: "100%",
            border: "none",
            borderRadius: "4px",
            display: "block",
            boxSizing: "border-box"
        });

        // Set iframe attributes for YouTube videos
        if (embedUrl.includes('youtube.com/embed/')) {
            iframe.setAttribute('allowfullscreen', '');
            iframe.setAttribute('allow', 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture');
        }

        iframe.src = embedUrl;

        // Clear previous content and add iframe
        this.htmlContainer.innerHTML = "";
        this.htmlContainer.appendChild(iframe);

        // Make sure htmlContainer takes full size
        Object.assign(this.htmlContainer.style, {
            width: "100%",
            height: "100%",
            margin: "0",
            padding: "0",
            display: "block",
            boxSizing: "border-box"
        });

        this.container.style.display = "flex";

        // Always center on screen
        this.container.style.top = "50%";
        this.container.style.left = "50%";
        this.container.style.transform = "translate(-50%, -50%)";

        // Set initial size of viewport
        const initialWidth = Math.floor(window.innerWidth * 0.55);
        const initialHeight = Math.floor(window.innerHeight * 0.65);

        this.container.style.width = initialWidth + "px";
        this.container.style.height = initialHeight + "px";

        this.container.style.resize = "both";
        this.collapsed = false;
        this.content.style.display = "block";
        this.collapseBtn.innerHTML = "&#x25B2;";
        this._originalSize = null;

        this.windowManager.setActivePopup(this);
        return this;
    }

    // Convert URLs to embeddable format
    convertToEmbeddableUrl(url) {
        // YouTube URL patterns to convert
        const youtubePatterns = [
            /(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([a-zA-Z0-9_-]+)/,
            /(?:https?:\/\/)?(?:www\.)?youtu\.be\/([a-zA-Z0-9_-]+)/,
            /(?:https?:\/\/)?(?:www\.)?youtube\.com\/embed\/([a-zA-Z0-9_-]+)/
        ];

        for (const pattern of youtubePatterns) {
            const match = url.match(pattern);
            if (match) {
                return `https://www.youtube.com/embed/${match[1]}`;
            }
        }

        // // Vimeo:
        // const vimeoPattern = /(?:https?:\/\/)?(?:www\.)?vimeo\.com\/(\d+)/;
        // const vimeoMatch = url.match(vimeoPattern);
        // if (vimeoMatch) {
        //     const videoId = vimeoMatch[1];
        //     return `https://player.vimeo.com/video/${videoId}`;
        // }

        // Return original URL if no conversion needed
        return url;
    }

    // Hide popup
    hide() {
        this.container.style.display = "none";
        return this;
    }

    // Destroy popup completely
    destroy() {
        // Stop any iframes/videos
        this.htmlContainer.innerHTML = "";

        // Remove resize observer
        if (this.resizeObserver) {
            this.resizeObserver.disconnect();
        }

        // Remove from DOM
        if (this.container.parentNode) {
            this.container.parentNode.removeChild(this.container);
        }
    }

    // Rest of your methods (toggleCollapse, updateSize, makeDraggable) stay the same...
    toggleCollapse() {
        this.collapsed = !this.collapsed;
        if (this.collapsed) {
            // Save current dimensions, but use original dimensions if we're currently out of bounds
            const currentHeight = this.container.style.height || this.container.offsetHeight + "px";
            const currentWidth = this.container.style.width || this.container.offsetWidth + "px";

            const heightToSave = this._originalSize ? this._originalSize.height + "px" : currentHeight;
            const widthToSave = this._originalSize ? this._originalSize.width + "px" : currentWidth;

            this._preCollapse = {
                height: heightToSave,
                width: widthToSave
            };

            this.content.style.display = "none";
            this.collapseBtn.innerHTML = "&#x25BC;"; // Down triangle
            this.container.style.height = this.header.offsetHeight + "px";
            this.container.style.minHeight = this.header.offsetHeight + "px";
            // Disable vertical resizing when collapsed
            this.container.style.resize = "horizontal";
        } else {
            this.content.style.display = "block";
            this.collapseBtn.innerHTML = "&#x25B2;"; // Up triangle
            // Restore previous height AND width (width might have been updated by resize observer)
            if (this._preCollapse) {
                this.container.style.height = this._preCollapse.height;
                this.container.style.width = this._preCollapse.width;
            }
            this.container.style.minHeight = "40px";
            // Re-enable both horizontal and vertical resizing
            this.container.style.resize = "both";

            // Clear the original size since we're restoring to the intended size
            this._originalSize = null;
        }

        // Immediately check bounds after collapse/expand
        this.updateSize();
    }

    // Update size based on bounds
    updateSize() {
        this._isOOBResizing = true; // SET FLAG BEFORE RESIZING

        const rect = this.container.getBoundingClientRect();
        const minWidth = parseInt(this.container.style.minWidth) || 400;
        const minHeight = parseInt(this.container.style.minHeight) || 40;
        const padding = 8;

        let left = rect.left, top = rect.top;
        let width = rect.width, height = rect.height;

        // Save original size when first going out of bounds
        const isOutOfBoundsRight = left + width > window.innerWidth - padding;
        const isOutOfBoundsBottom = top + height > window.innerHeight - padding;

        if ((isOutOfBoundsRight || (!this.collapsed && isOutOfBoundsBottom)) && !this._originalSize) {
            this._originalSize = { width, height };
        }

        // Calculate available space
        const availableWidth = window.innerWidth - left - padding;
        const availableHeight = window.innerHeight - top - padding;

        // If we have original size and there's more space available, grow towards original
        if (this._originalSize) {
            if (availableWidth >= this._originalSize.width && (!this.collapsed && availableHeight >= this._originalSize.height)) {
                // Full space available, restore original size
                width = this._originalSize.width;
                if (!this.collapsed) {
                    height = this._originalSize.height;
                }
                this._originalSize = null;
            } else {
                // Partial space, grow as much as possible towards original
                width = Math.min(this._originalSize.width, Math.max(minWidth, availableWidth));
                if (!this.collapsed) {
                    height = Math.min(this._originalSize.height, Math.max(minHeight, availableHeight));
                }
            }
        } else {
            // Shrink if out of bounds
            if (isOutOfBoundsRight) {
                width = Math.max(minWidth, availableWidth);
            }
            if (!this.collapsed && isOutOfBoundsBottom) {
                height = Math.max(minHeight, availableHeight);
            }
        }

        // Apply size
        this.container.style.width = width + "px";
        this.container.style.height = height + "px";

        // Use setTimeout to clear flag after the resize has been applied
        setTimeout(() => {
            this._isOOBResizing = false;
        }, 0);
    }

    // Make the popup draggable with boundary constraints
    makeDraggable() {
        let offsetX, offsetY, isDragging = false;

        this.header.onmousedown = (e) => {
            if (e.target === this.closeBtn || e.target === this.collapseBtn) return;

            isDragging = true;
            offsetX = e.clientX - this.container.getBoundingClientRect().left;
            offsetY = e.clientY - this.container.getBoundingClientRect().top;

            document.onmousemove = (e) => {
                if (!isDragging) return;

                const padding = 8;
                const minWidth = parseInt(this.container.style.minWidth) || 400;
                const minHeight = parseInt(this.container.style.minHeight) || 40;

                let newLeft = e.clientX - offsetX;
                let newTop = e.clientY - offsetY;

                // Constrain to viewport bounds
                newLeft = Math.max(padding, Math.min(newLeft, window.innerWidth - minWidth - padding));
                newTop = Math.max(padding, Math.min(newTop, window.innerHeight - minHeight - padding));

                this.container.style.left = newLeft + "px";
                this.container.style.top = newTop + "px";
                this.container.style.transform = "none";

                this.updateSize();
            };

            document.onmouseup = () => {
                isDragging = false;
                document.onmousemove = null;
                document.onmouseup = null;
            };
        };
    }
}

export { HTMLPopup };

