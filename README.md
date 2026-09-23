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
