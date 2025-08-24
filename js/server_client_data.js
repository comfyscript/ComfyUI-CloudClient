// Client-side JavaScript for handling image downloads from Kaggle ComfyUI
import { app } from "../../../scripts/app.js";
import { api } from "../../../scripts/api.js";

console.log("This is the app: ",window.comfyAPI.app.app)
console.log("This is the api: ",window.comfyAPI.api)

// This is the lite graph
const litegraph = window.comfyAPI.app.app.graph;
console.log("lite graph is here: ",litegraph)

// Add event listener for our custom node's messages
app.registerExtension({
    name: "ServerClientConnection",
    setup() {
        // Listen for image data from the server
        api.addEventListener("server_client_data", (event) => {
            const { files } = event.detail;

            // Using files to output file downloading instead
            files.forEach(file => {
                const { filename, format, data } = file;
                downloadFile(filename, format, data)
            })
        });

        // Listen for error messages
        api.addEventListener("server_client_data_error", (event) => {
            console.error("Unable to save data locally:", event.detail.message);
            // Optionally display error to user
            app.ui.notifications.create("Error saving locally: " + event.detail.message, "error", 5000);
        });
    }
});

const getMineType = (format)=>{
    // Creating a mineType
    const mineTypes = {
        png:"image/png",
        gif:"image/gif",
        jpg:"image/jpg",
        jpeg:"image/jpeg",
        webm:"video/webm",
        mp4:"video/mp4",
        webp:"image/webp",
        pdf:"application/pdf",
        text:"text/plain",
        json:"application/json"
    }
    return mineTypes[format.toLowerCase()]||"application/octet-stream"
}

// Download file from ComfyUI must be in base64Data or Raw Data
function downloadFile(filename, format, base64DataOrRaw) {
    const link = document.createElement('a');
    // Do not display the link on page
    link.style.display = "none";
    // Generating the href link
    link.href = `data:${getMineType(format)};base64,${base64DataOrRaw}`;
    link.download = filename;

    // Triggering file name download
    console.log('downloading: ' + filename);

    // Append to document, click, and remove
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}
