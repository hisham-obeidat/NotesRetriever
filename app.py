"""
app.py — local search web app over slides.db (FTS5-indexed course slides)

Run:
    python app.py

Then open http://127.0.0.1:5000 in your browser.

Expects slides.db (with the `slides_fts5` FTS5 virtual table already built,
same schema/table produced by ingest.py) to be in the same folder as this
file — or set SLIDES_DB env var to point elsewhere.
"""

import os
import re
import sqlite3
import pymupdf
from flask import Flask, jsonify, render_template, request
from pptx import Presentation

DB_PATH = os.environ.get("SLIDES_DB", os.path.join(os.path.dirname(__file__), "slides.db"))

app = Flask(__name__)

def refresh_ingestion():
    def get_metadata(full_path, root):
        rel_path = os.path.relpath(full_path, root)
        parts = os.path.normpath(rel_path).split(os.sep)

        filename = parts[-1]
        year = parts[0] if len(parts) > 0 else None
        semester = parts[1] if len(parts) > 1 else None
        course = parts[2] if len(parts) > 2 else None
        topic = " / ".join(parts[3:-1]) if len(parts) > 4 else (parts[3] if len(parts) == 4 else None)

        return [year, semester, course, topic, filename]
        
    def extract_pdf_text(pdf_path):
        doc = pymupdf.open(pdf_path)
        pages = []
        for page_num, page in enumerate(doc, start=1):
            text = page.get_text()
            pages.append((page_num, text))
        doc.close()
        return pages
        
    def extract_pptx_text(pptxPath):
        prs = Presentation(pptxPath)
        slides = []
        for page_num, slide in enumerate(prs.slides, start=1):
            text = []
            for shape in slide.shapes:
                if shape.has_text_frame:
                    text.append(shape.text_frame.text)
            slides.append((page_num, "\n".join(text)))
        return slides
                
    root = "C:/Users/obeid/OneDrive/Documents/Desktop/PSUT"
    all_data = []
    
    conn = get_conn()
    cur = conn.cursor()
    
    cur.execute("SELECT DISTINCT filepath FROM slides")
    already_ingested = set(row[0] for row in cur.fetchall())
    for dirpath, dirnames, filenames in os.walk(root):
        for filename in filenames:
            full_path = os.path.join(dirpath, filename)
            rel_path = os.path.relpath(full_path, root)
            if rel_path in already_ingested:
                continue
            if filename.endswith(".pdf") or filename.endswith(".pptx"):
                full_path = os.path.join(dirpath, filename)
                meta_data = get_metadata(full_path, root)
                pages = []
                if filename.endswith(".pdf"):
                    pages = extract_pdf_text(full_path)
                elif filename.endswith(".pptx"):
                    pages = extract_pptx_text(full_path)
                
                for page_num, text in pages:
                    text = re.sub(r'\s+', ' ', text).strip()
                    if text== '':
                        continue
                    row = meta_data + [page_num, text, rel_path]
                    all_data.append(row)
    if all_data:
        cur.executemany("INSERT INTO slides (year, semester, course, topic, filename, pageNum, text, filePath) VALUES (?, ? ,? ,? ,? ,?, ?, ?)",
                        all_data)
        cur.executemany("INSERT INTO slides_fts5 (text, year, semester, course, topic, filename, pageNum) VALUES (?, ? ,? ,? ,? ,?, ?)",
                                [(r[6], r[0], r[1], r[2], r[3], r[4], r[5]) for r in all_data])
        conn.commit()
        print("new files added")
    else:
        print("No new files")

        
       
        


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def sanitize_fts_query(q: str) -> str:
    """
    Turn free-text user input into a safe FTS5 MATCH query.
    Strips FTS5 special characters and wraps each token in quotes so things
    like punctuation or a lone '-' don't blow up the query syntax, and adds
    a trailing '*' to the last token for prefix matching (so partial words
    while typing still return results).
    """
    tokens = re.findall(r"\w+", q)
    if not tokens:
        return ""
    quoted = [f'"{t}"' for t in tokens]
    return " ".join(quoted)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/search")
def api_search():
    raw_query = request.args.get("q", "").strip()
    course_filter = request.args.get("course", "").strip()
    limit = min(int(request.args.get("limit", 25)), 100)

    if not raw_query:
        return jsonify({"query": raw_query, "results": [], "count": 0})

    fts_query = sanitize_fts_query(raw_query)
    if not fts_query:
        return jsonify({"query": raw_query, "results": [], "count": 0})

    conn = get_conn()
    cur = conn.cursor()

    sql = """
        SELECT year, semester, course, topic, filename, pageNum,
               snippet(slides_fts5, 0, '<mark>', '</mark>', '…', 12) AS snippet,
               bm25(slides_fts5) AS score
        FROM slides_fts5
        WHERE slides_fts5 MATCH ?
    """
    params = [fts_query]

    if course_filter:
        sql += " AND course = ?"
        params.append(course_filter)

    sql += " ORDER BY score LIMIT ?"
    params.append(limit)

    try:
        cur.execute(sql, params)
        rows = cur.fetchall()
    except sqlite3.OperationalError as e:
        conn.close()
        return jsonify({"query": raw_query, "results": [], "count": 0, "error": str(e)}), 400

    results = [
        {
            "year": row["year"],
            "semester": row["semester"],
            "course": row["course"],
            "topic": row["topic"],
            "filename": row["filename"],
            "pageNum": row["pageNum"],
            "snippet": row["snippet"],
        }
        for row in rows
    ]
    conn.close()

    return jsonify({"query": raw_query, "results": results, "count": len(results)})


@app.route("/api/courses")
def api_courses():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT course FROM slides WHERE course IS NOT NULL ORDER BY course")
    courses = [row[0] for row in cur.fetchall()]
    conn.close()
    return jsonify({"courses": courses})


if __name__ == "__main__":
    if not os.path.exists(DB_PATH):
        print(f"Warning: {DB_PATH} not found. Place slides.db next to app.py, "
              f"or set the SLIDES_DB environment variable.")
    refresh_ingestion()
    app.run(debug=True)
