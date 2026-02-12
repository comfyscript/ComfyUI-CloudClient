import { app } from "../../../scripts/app.js";

app.registerExtension({
    name: "example.imagepreview",

    async setup() {
        // Listen for preview updates from the server
        function handlePreviewUpdate(event) {
            const { image, node_id } = event.detail;

            // Find the specific node that matches this node_id
            const nodes = app.graph._nodes;
            for (const node of nodes) {
                if (node.type === "TemporaryImagePreview" && node.pythonNodeId === node_id) {
                    // Add or update the preview image
                    if (!node.previewWidget) {
                        // Create preview widget on first use
                        node.previewWidget = node.addDOMWidget(
                            "preview",
                            "preview",
                            document.createElement("img")
                        );
                        node.previewWidget.element.style.width = "100%";
                        node.previewWidget.element.style.height = "auto";
                    }

                    // Update the image source
                    node.previewWidget.element.src = image;
                    node.setSize([node.size[0], node.size[1]]);
                    break; // Found the matching node, stop searching
                }
            }
        }

        app.api.addEventListener("imagepreview.update", handlePreviewUpdate);
    },

    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "TemporaryImagePreview") {
            const onNodeCreated = nodeType.prototype.onNodeCreated;

            nodeType.prototype.onNodeCreated = function() {
                const result = onNodeCreated?.apply(this, arguments);

                // Set initial size for the node
                this.setSize([300, 200]);

                return result;
            };

            // Store the Python node ID when execution happens
            const onExecuted = nodeType.prototype.onExecuted;
            nodeType.prototype.onExecuted = function(message) {
                // Store a unique identifier for this node instance
                this.pythonNodeId = String(this.id);

                onExecuted?.apply(this, arguments);
            };
        }
    }
});
