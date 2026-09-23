# NotesRetriever 📝

A fast, web-based retrieval system designed to efficiently ingest, organize, and query notes. This project processes raw text data and provides an intuitive search interface to instantly surface relevant information.

##Features
* **Automated Data Ingestion:** Process and index raw notes seamlessly using the built-in ingestion pipeline.
* **Fast Querying:** Instantly search through your stored notes repository.
* **Web Interface:** A clean, user-friendly front-end for entering queries and viewing results.

##Project Structure
* `app.py`: The main web server application Flask that handles search requests and serves the UI.
* `ingestion.ipynb`: A Jupyter Notebook containing the data processing pipeline used to clean, embed, or index the notes before querying.
* `Templates/index.html`: The front-end HTML interface where users interact with the search system.

##Tech Stack
* **Language:** Python
* **Web Framework:** Flask
* **Data Processing:** Jupyter Notebook, Pymupdf, pptx

## 🗂️ Data Architecture

**Note on Data:** This is a personal project, and the database is built entirely from my own university notes. The underlying database files are excluded from this repository for privacy. 
To run the `ingestion.ipynb` pipeline locally, you will need to supply your own `.pptx` or `.pdf` files, and **update the root directory path in the notebook** to point to your local folder.
The ingestion script expects the raw data to follow a strict hierarchical folder structure:
**`Year -> Semester -> Course -> Topic (Optional) -> File`**
Here is an example of the expected directory tree. In this case, the root path variable in your ingestion notebook should be set to `Notes_Database`:
```
Notes_Database/
├── 2025/
│   ├── Spring/
│   │   ├── Deep_Learning/
│   │   │   ├── CNN_Architectures/
│   │   │   │   └── module_4_slides.pptx
│   │   │   └── Regularization/
│   │   │       └── notes.pdf
│   │   └── Big_Data_Processing/
│   │       ├── Apache_Spark/
│   │       │   └── cluster_setup.pptx
│   │       └── lecture_01.pdf     <-- (Topic folder is optional)
-> In this case the root should be Notes_Database
