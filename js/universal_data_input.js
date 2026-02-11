import { app } from "../../../scripts/app.js";

app.registerExtension({
    name: "custom.inputDataToImage",

    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "UniversalDataToImage") {
            const onNodeCreated = nodeType.prototype.onNodeCreated;

            nodeType.prototype.onNodeCreated = function() {
                const result = onNodeCreated?.apply(this, arguments);

                // Find the data_uri widget
                const dataUriWidget = this.widgets.find(w => w.name === "data_uri");

                if (dataUriWidget) {
                    // Store original callback
                    const originalCallback = dataUriWidget.callback;

                    // Add paste event listener to the widget's input element
                    const setupPasteHandler = () => {
                        const inputElement = dataUriWidget.inputEl;
                        if (inputElement) {
                            inputElement.addEventListener('paste', async (e) => {
                                const items = e.clipboardData?.items;
                                if (!items) return;

                                // Check if there's an image in the clipboard
                                let hasImage = false;
                                for (let i = 0; i < items.length; i++) {
                                    if (items[i].type.indexOf('image') !== -1) {
                                        hasImage = true;

                                        // Only prevent default if we found an image
                                        e.preventDefault();

                                        const blob = items[i].getAsFile();

                                        // Convert blob to data URI
                                        const reader = new FileReader();
                                        reader.onload = (event) => {
                                            const dataUri = event.target.result;
                                            dataUriWidget.value = dataUri;

                                            // Trigger the original callback if it exists
                                            if (originalCallback) {
                                                originalCallback(dataUri);
                                            }
                                        };
                                        reader.readAsDataURL(blob);

                                        break;
                                    }
                                }

                                // If no image found, let default paste behavior continue
                                // (this allows text/data URIs to be pasted normally)
                            });
                        }
                    };

                    // Setup immediately and also watch for widget DOM creation
                    setTimeout(setupPasteHandler, 100);
                }

                return result;
            };
        }
    }
});
