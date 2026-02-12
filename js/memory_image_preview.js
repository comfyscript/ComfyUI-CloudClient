import { app } from "../../../scripts/app.js";

app.registerExtension({
    name: "example.imagepreview",

    async setup() {
        // Listen for preview updates from the server
        function handlePreviewUpdate(event) {
            const { image, node_id } = event.detail;

            // Find all nodes and update ONLY the matching one
            const nodes = app.graph._nodes;
            for (const node of nodes) {
                if (node.type === "TemporaryImagePreview" && node.id == node_id) {
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

                    // Exit after finding the correct node
                    break;
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
        }
    }
});
