<p>
  <div align="center">
  <h1>
<br >
    DOCS GPT - Setup Guide<br /> <br />
    <a href="https://github.com/psf/black">
      <img
        src="https://img.shields.io/badge/code%20style-black-000000.svg"
        alt="The Uncompromising Code Formatter"
      />
    </a>
      <a>
      <img
        src="https://img.shields.io/badge/python-3.9%20%7C%203.10-blue"
        alt="Python Versions"
      />
    </a>
     <a href="https://opensource.org/licenses/MIT">
      <img
        src="https://img.shields.io/badge/License-MIT-blue.svg"
        alt="License: MIT"
      />
    </a>
  </h1>
      
  </div>
  <h3>Welcome to the setup guide for the DOCS GPT Module. Follow these steps to get your environment ready and run the application.</h3>
</p>

---
## Prerequisites
- Ensure you have Git installed on your system.
- Python 3 should be installed on your system.

## Step 1: Clone the Repository
First, clone the repository to your local machine using Git. Open your terminal and run:

```
git clone https://github.com/infocodiste/DocsGpt.git
```

## Step 2: Create a Virtual Environment
Creating a virtual environment is crucial to manage dependencies.

### For Mac & Linux:
Run the following commands:

```
python3 -m venv env/doc_gpt
source env/doc_gpt/bin/activate
```

### For Windows:
Run these commands in your Command Prompt or PowerShell:

```
python -m venv env\doc_gpt
.\env\doc_gpt\Scripts\activate
```

With your virtual environment active, install the required Python packages:


#### For Windows:
```
pip install -r requirements.txt
```

#### For Mac & Linux:
```
pip3 install -r requirements.txt
```

## Step 3: Run the Application
Finally, start the application with the following command:

#### For Windows:
```
python app.py
```

#### For Mac & Linux:
```
python3 app.py
```

## API Endpoints:
  - The application provides the following endpoints:
### /add_docs
- **Method**: POST
- **Description**: This endpoint generates embeddings for a given document. Supports PDF and DOCX files..
- **Request Body**:
  ```json
  {
    "docs_url": "https://example.com/document.pdf"
  }
  ```
- **Response**:
  - **Success**:
     ```json
    {
      "data": {
          "batch_id": "5f0c6a9a-0e99-4072-ab37-646a98d2f465",
          "document_url": "https://example.com/document.pdf"
      },
      "message": "Embeddings generated successfully",
      "status": true
    }
    ```
  - **Error**:
    ```json
    {
      "data": {},
      "message": "Invalid document format, Supported formats are PDF and DOCX.",
      "status": false
    }
    ```

### /chat
- **Method**: POST
- **Description**: TThis endpoint allows chatting with the document database using the generated embeddings.
- **Request Body**:
  ```json
  {
    "query":"Your question here",
    "batch_id":"User batch_id"
  }
  ```
- **Response**:
  - **Success**:
     ```json
    {
      "data": "Response to the query",
      "message": "Success",
      "status": true
    }
    ```
  - **Error**:
    ```json
    {
      "status": false,
      "message": "Error message",
      "data": {}
    }
    ```

## Conclusion
Your setup is now complete! If you encounter any issues, submit an issue on the GitHub repository.
---
