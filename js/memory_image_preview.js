import { app } from "../../../scripts/app.js";

// Helper function to find node by execution ID (handles subgraphs)
function findNodeByExecutionId(executionId, graph = app.graph) {
    const idPath = String(executionId).split(':').map(id => parseInt(id));

    // Walk down the execution path
    let currentGraph = graph;
    let targetNode = null;

    for (let i = 0; i < idPath.length; i++) {
        const nodeId = idPath[i];

        // Find node in current graph level
        targetNode = (currentGraph._nodes || currentGraph.nodes || []).find(n => n.id === nodeId);

        if (!targetNode) {
            return null;
        }

        // If this is not the last ID in path, descend into subgraph
        if (i < idPath.length - 1) {
            if (!targetNode.subgraph) {
                return null;
            }
            currentGraph = targetNode.subgraph;
        }
    }

    // Only return if it's the right node type
    return targetNode?.type === "TemporaryImagePreview" ? targetNode : null;
}

app.registerExtension({
    name: "example.imagepreview",

    async setup() {
        // Listen for preview updates from the server
        function handlePreviewUpdate(event) {
            const { image, node_id } = event.detail;

            // Find the matching node using execution ID path
            const targetNode = findNodeByExecutionId(node_id);

            if (targetNode) {
                // Add or update the preview image
                if (!targetNode.previewWidget) {
                    // Create preview widget on first use
                    targetNode.previewWidget = targetNode.addDOMWidget(
                        "preview",
                        "preview",
                        document.createElement("img")
                    );
                    targetNode.previewWidget.element.style.width = "100%";
                    targetNode.previewWidget.element.style.height = "auto";
                }

                // Update the image source
                targetNode.previewWidget.element.src = image;
                targetNode.setSize([targetNode.size[0], targetNode.size[1]]);
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
