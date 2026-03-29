# Static Handwriting Recognition Project

![TextScribe OCR Overview](A.png)

A clean, modern, and privacy-focused handwriting recognition system that runs entirely in your web browser. This project allows users to convert images of their handwritten notes into editable digital text using client-side AI technologies.

## 🚀 Project Overview

The Handwriting Recognition System was originally conceived as a deep learning application but has been refactored into a completely static, frontend-only application for maximum portability and ease of use. 

Thanks to the integration of **Tesseract.js**, the Optical Character Recognition (OCR) model executes directly in the user's browser without requiring any backend server or API calls. Your images never leave your computer, ensuring complete privacy and fast processing times.

## ✨ Features

- **Client-Side OCR**: Perform accurate image-to-text recognition seamlessly using Tesseract.js.
- **100% Offline Capable**: Because everything runs in the browser, the application works securely without an active internet connection (after initial load).
- **Privacy First**: Sensitive documents and personal notes are never uploaded to a remote server.
- **Beautiful UX/UI**: Enjoy dynamic animations, loading indicators, and smart toasts notifications, built via vanilla HTML, CSS, and JS.
- **Output Management**: Users can preview their processed text, copy to clipboard, or download directly to a `.txt` file effortlessly.

## 📁 Folder Structure

The project has been architected to natively support static web hosting platforms such as GitHub Pages:

```text
├── index.html       # Landing page detailing system capabilities
├── upload.html      # The central workspace to drag-and-drop/upload images for OCR
├── about.html       # Learn more about the project and team behind it
├── 404.html         # Custom fast HTTP 404 error page 
├── css/             # All CSS styles including animations and dynamic typography
│   └── style.css
├── js/              # Application logic files
│   ├── main.js      # Global UI orchestration
│   └── upload.js    # Specialized logic for file upload and Tesseract.js OCR handling
├── assets/          # Static elements (logos, hero graphics)
└── README.md        # Project documentation
```

## ⚙️ Setup and Usage Instructions

Because this project is fundamentally stateless and static, there are no dependencies to install via `npm`, `pip`, or servers to provision.

**To run the application locally on your machine:**
1. Clone or download this repository.
2. Open `index.html` directly in any modern JavaScript-enabled web browser.
3. Click on the **Upload** page within the navigation bar.
4. Drag and drop any `.jpg`, `.png`, or `.bmp` file, then click "Convert to Text".

*Note:* If you encounter Cross-Origin Resource Sharing (CORS) errors running the `.html` file directly when loading `Tesseract.js` worker processes, you may spawn a localized server using:
```bash
# Python 3
python -m http.server
```
or 
```bash
# Node
npx serve .
```

## 🌐 Steps to Deploy on GitHub Pages

You can easily host this application on the free tier of GitHub Pages since it has no backend dependencies natively.

1. Create a modern GitHub repository and upload all project files (maintaining the folder structure detailed above).
2. Once pushed, navigate to your repository's **Settings** tab on GitHub.
3. Below the left sidebar, click on **Pages** (under the "Code and automation" section).
4. Beneath **Build and deployment**, select **"Deploy from a branch"** as the Source.
5. In the **Branch** dropdown, pick your main branch (e.g., `main` or `master`) and select the `/ (root)` directory. Click **Save**.
6. Wait 1-2 minutes for the deployment action to run. A URL will be displayed indicating where your live site is accessible (e.g., `https://<username>.github.io/<repo-name>/`).

---
**Made with ❤️ for Academic Learning & Open-Source!**
