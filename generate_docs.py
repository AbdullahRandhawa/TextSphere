"""
generate_docs.py — Generates a professional, publication-ready DOCX technical documentation
for the TextSphere Multi-Model NLP & LLM Platform.
"""

import os
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn


def set_cell_background(cell, hex_color):
    """Sets background color of a table cell."""
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    tc_pr.append(shd)


def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Sets inner padding for a table cell."""
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_mar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{top}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'<w:left w:w="{left}" w:type="dxa"/>'
        f'<w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tc_pr.append(tc_mar)


def set_cell_border(cell, **kwargs):
    """Sets borders for a cell (top, bottom, left, right)."""
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'<w:top w:val="{kwargs.get("top", "single")}" w:sz="{kwargs.get("top_sz", "4")}" w:space="0" w:color="{kwargs.get("top_color", "CCCCCC")}"/>'
        f'<w:left w:val="{kwargs.get("left", "none")}" w:sz="0" w:space="0" w:color="auto"/>'
        f'<w:bottom w:val="{kwargs.get("bottom", "single")}" w:sz="{kwargs.get("bottom_sz", "4")}" w:space="0" w:color="{kwargs.get("bottom_color", "CCCCCC")}"/>'
        f'<w:right w:val="{kwargs.get("right", "none")}" w:sz="0" w:space="0" w:color="auto"/>'
        f'</w:tcBorders>'
    )
    tc_pr.append(tc_borders)


def build_documentation():
    doc = Document()

    # ---------------- Page Setup (1-inch margins) ----------------
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    # ---------------- Style Definitions ----------------
    styles = doc.styles

    # Normal text style
    normal_style = styles['Normal']
    normal_font = normal_style.font
    normal_font.name = 'Calibri'
    normal_font.size = Pt(10.5)
    normal_font.color.rgb = RGBColor(0x22, 0x22, 0x22)
    normal_style.paragraph_format.line_spacing = 1.15
    normal_style.paragraph_format.space_after = Pt(6)

    # Helper function for adding styled Headings
    def add_h1(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(18)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.name = 'Calibri'
        run.font.size = Pt(16)
        run.font.bold = True
        run.font.color.rgb = RGBColor(0x11, 0x11, 0x11)
        
        # Add a sleek underline border under H1
        pBdr = parse_xml(f'<w:pBdr {nsdecls("w")}><w:bottom w:val="single" w:sz="8" w:space="4" w:color="333333"/></w:pBdr>')
        p._p.get_or_add_pPr().append(pBdr)
        return p

    def add_h2(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.name = 'Calibri'
        run.font.size = Pt(13)
        run.font.bold = True
        run.font.color.rgb = RGBColor(0x22, 0x22, 0x22)
        return p

    def add_h3(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.name = 'Calibri'
        run.font.size = Pt(11)
        run.font.bold = True
        run.font.color.rgb = RGBColor(0x44, 0x44, 0x44)
        return p

    def add_code_block(code_text):
        tbl = doc.add_table(rows=1, cols=1)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = tbl.cell(0, 0)
        set_cell_background(cell, "F4F5F7")
        set_cell_margins(cell, top=120, bottom=120, left=200, right=200)
        set_cell_border(cell, top="single", top_sz="4", top_color="D0D5DD",
                              bottom="single", bottom_sz="4", bottom_color="D0D5DD")
        
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.0
        run = p.add_run(code_text.strip())
        run.font.name = 'Consolas'
        run.font.size = Pt(9.0)
        run.font.color.rgb = RGBColor(0x1F, 0x24, 0x2E)
        doc.add_paragraph() # Spacing after table

    # ---------------- DOCUMENT TITLE & HEADER ----------------
    title_p = doc.add_paragraph()
    title_p.paragraph_format.space_before = Pt(24)
    title_p.paragraph_format.space_after = Pt(4)
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    t_run = title_p.add_run("TEXTSPHERE")
    t_run.font.name = 'Calibri'
    t_run.font.size = Pt(26)
    t_run.font.bold = True
    t_run.font.color.rgb = RGBColor(0x11, 0x11, 0x11)

    sub_p = doc.add_paragraph()
    sub_p.paragraph_format.space_before = Pt(0)
    sub_p.paragraph_format.space_after = Pt(18)
    sub_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub_run = sub_p.add_run("Comprehensive Technical Developer Guide & System Architecture")
    sub_run.font.name = 'Calibri'
    sub_run.font.size = Pt(14)
    sub_run.font.color.rgb = RGBColor(0x55, 0x55, 0x55)

    # Metadata Table
    meta_table = doc.add_table(rows=4, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_data = [
        ("Project Name", "TextSphere NLP & LLM Platform"),
        ("System Architecture", "Dual-Engine (Local Fine-Tuned Transformers + Cloud LLM Streaming)"),
        ("Technology Stack", "FastAPI, PyTorch, HuggingFace Transformers, React 18, Vite, Firebase"),
        ("Repository", "https://github.com/AbdullahRandhawa/TextSphere"),
    ]
    for row_idx, (k, v) in enumerate(meta_data):
        cell_k = meta_table.cell(row_idx, 0)
        cell_v = meta_table.cell(row_idx, 1)
        cell_k.width = Inches(2.2)
        cell_v.width = Inches(4.3)
        
        set_cell_background(cell_k, "F8F9FA")
        set_cell_margins(cell_k, top=60, bottom=60, left=100, right=100)
        set_cell_margins(cell_v, top=60, bottom=60, left=100, right=100)
        set_cell_border(cell_k, top="single", bottom="single", top_color="E0E0E0", bottom_color="E0E0E0")
        set_cell_border(cell_v, top="single", bottom="single", top_color="E0E0E0", bottom_color="E0E0E0")

        pk = cell_k.paragraphs[0]
        pk.paragraph_format.space_after = Pt(0)
        rk = pk.add_run(k)
        rk.font.bold = True
        rk.font.size = Pt(9.5)

        pv = cell_v.paragraphs[0]
        pv.paragraph_format.space_after = Pt(0)
        rv = pv.add_run(v)
        rv.font.size = Pt(9.5)

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # =========================================================================
    # SECTION 1: EXECUTIVE SUMMARY & ARCHITECTURAL OVERVIEW
    # =========================================================================
    add_h1("1. Executive Summary & Architectural Overview")
    
    doc.add_paragraph(
        "TextSphere is an enterprise-grade, full-stack Natural Language Processing (NLP) and Conversational AI "
        "workspace designed to overcome the critical latency, privacy, and cost bottlenecks associated with monolithic "
        "cloud LLMs. Rather than routing all specialized NLP tasks to large API-based models, TextSphere implements "
        "a Dual-Engine Hybrid Architecture:"
    )

    p_b1 = doc.add_paragraph(style='List Bullet')
    r = p_b1.add_run("Locally Hosted Fine-Tuned Transformer Models: ")
    r.font.bold = True
    p_b1.add_run("Dedicated, parameter-efficient neural networks (DistilBERT, BERT, T5) perform specialized inference "
                 "(sentiment classification, entity extraction, question answering, summarization, and topic identification) "
                 "with ultra-low latency and zero token costs.")

    p_b2 = doc.add_paragraph(style='List Bullet')
    r = p_b2.add_run("Cloud LLM Streaming Commentary: ")
    r.font.bold = True
    p_b2.add_run("A conversational Large Language Model (via OpenRouter) contextualizes and elaborates upon the structured "
                 "outputs produced by the local tools, streaming insights asynchronously via Server-Sent Events (SSE).")

    p_b3 = doc.add_paragraph(style='List Bullet')
    r = p_b3.add_run("Enterprise Persistence & Security: ")
    r.font.bold = True
    p_b3.add_run("Firebase Authentication ensures secure session management, while Google Cloud Firestore asynchronously "
                 "persists user chats, tool results, and rate-limiting counters.")

    # =========================================================================
    # SECTION 2: MACHINE LEARNING & FINE-TUNED MODELS SPECIFICATION
    # =========================================================================
    add_h1("2. Machine Learning Architecture & Fine-Tuned NLP Tools")
    
    doc.add_paragraph(
        "TextSphere hosts five distinct transformer architectures locally. Each model has been fine-tuned on "
        "industry-benchmark NLP datasets and exported to the PyTorch Safetensors format for maximum safety and loading speed."
    )

    # Table of models
    tbl_models = doc.add_table(rows=6, cols=5)
    tbl_models.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers = ["NLP Tool", "Base Model", "Fine-Tuned Dataset", "Task Objective", "Output Schema"]
    for c_idx, h in enumerate(headers):
        cell = tbl_models.cell(0, c_idx)
        set_cell_background(cell, "1F242E")
        set_cell_margins(cell, top=100, bottom=100, left=100, right=100)
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(h)
        r.font.bold = True
        r.font.size = Pt(9.0)
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    models_data = [
        ("Sentiment Analyzer", "DistilBERT uncased", "SST-2 (Stanford Sentiment)", "Binary Polarity Detection", "label (Positive/Negative), confidence"),
        ("Topic Classifier", "DistilBERT uncased", "AG News", "4-class Classification", "label (World/Sports/Biz/Sci), confidence"),
        ("Named Entity (NER)", "BERT cased", "CoNLL-2003", "Token Span Extraction", "entities: [{text, label, start, end}]"),
        ("Summarizer", "T5-small", "CNN / DailyMail", "Abstractive Summarization", "summary (string)"),
        ("Question Answering", "DistilBERT cased", "SQuAD v1.1", "Extractive Span Answer", "answer (string), confidence"),
    ]

    for r_idx, row_data in enumerate(models_data, start=1):
        bg = "FFFFFF" if r_idx % 2 != 0 else "F8F9FA"
        for c_idx, val in enumerate(row_data):
            cell = tbl_models.cell(r_idx, c_idx)
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=80, bottom=80, left=80, right=80)
            set_cell_border(cell, top="single", bottom="single", top_color="E0E0E0", bottom_color="E0E0E0")
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            r = p.add_run(val)
            r.font.size = Pt(8.5)

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    add_h2("2.1 In-Place Memory Loader & Zero-Copy Architecture")
    doc.add_paragraph(
        "To prevent duplicate disk allocation and operating system temp-file accumulation, the backend implements an optimized "
        "in-place loader (app/tools/_loader.py). The loader verifies checkpoint integrity (*.safetensors, config.json, tokenizer.json) "
        "directly in the finetuned_models repository tree and initializes HuggingFace instances without temporary file copies. "
        "A process-lifetime cache ensures each neural network is instantiated exactly once during server startup."
    )

    add_h2("2.2 Google Colab Fine-Tuning Pipelines")
    doc.add_paragraph(
        "Training notebooks are organized in the finetune_notebooks/ directory. Each notebook contains a full reproducible "
        "pipeline including dataset downloading, HuggingFace FastTokenizer mapping, learning rate warmups with AdamW, "
        "evaluation against validation sets, and final checkpoint export."
    )

    # =========================================================================
    # SECTION 3: BACKEND ARCHITECTURE (FastAPI & ASYNC CORE)
    # =========================================================================
    add_h1("3. Backend Architecture (FastAPI & Asynchronous Core)")
    
    doc.add_paragraph(
        "The backend is built with FastAPI and asynchronous Python 3.10+. It utilizes asynchronous non-blocking I/O "
        "for Firestore and OpenRouter interactions while executing local PyTorch inference under torch.no_grad() contexts."
    )

    add_h2("3.1 Server-Sent Events (SSE) Streaming Pipeline")
    doc.add_paragraph(
        "The core communication protocol between the client and the backend is an SSE stream (POST /chat). "
        "The execution flow operates as follows:"
    )

    flow_steps = [
        ("Authentication & Rate Limiting", "Bearer JWT verified against Firebase Auth; user limits checked in parallel."),
        ("Local Tool Execution", "If toolId is specified, the dedicated model runs inference and emits a tool_result event containing predictions, base model metadata, and confidence."),
        ("Asynchronous LLM Streaming", "Conversation history (up to CONTEXT_MESSAGE_COUNT) plus tool output are formatted into an LLM prompt. Chunks are streamed as commentary_chunk events."),
        ("Parallel Persistence", "User message, assistant response, tool metadata, and usage counters are persisted concurrently to Firestore via asyncio.gather."),
        ("Stream Finalization", "Emits a done event to signal completion to the client UI."),
    ]
    for title, desc in flow_steps:
        p = doc.add_paragraph(style='List Bullet')
        r = p.add_run(f"{title}: ")
        r.font.bold = True
        p.add_run(desc)

    add_h2("3.2 SSE Event Schema Reference")
    add_code_block("""// 1. Tool Result Event (Local Transformer Output)
data: {"event": "tool_result", "tool_id": "sentiment", "display_name": "Sentiment Analyzer", 
       "base_model": "DistilBERT", "fine_tune_dataset": "SST-2", 
       "result": {"label": "Positive", "confidence": 0.9987}}

// 2. Commentary Chunk Event (Cloud LLM Stream)
data: {"event": "commentary_chunk", "text": "The input expression reveals..."}

// 3. Completion Event
data: {"event": "done"}""")

    # =========================================================================
    # SECTION 4: SECURITY & PERSISTENCE LAYER (FIREBASE)
    # =========================================================================
    add_h1("4. Security & Persistence Layer (Firebase)")

    doc.add_paragraph(
        "TextSphere delegates authentication and primary data persistence to Google Firebase, utilizing the "
        "Firebase Admin SDK for server-side token validation and secure Firestore reads/writes."
    )

    add_h2("4.1 Firestore Database Schema")
    doc.add_paragraph(
        "Data is organized hierarchically to enforce strict per-user authorization boundaries:"
    )

    tbl_schema = doc.add_table(rows=3, cols=3)
    tbl_schema.alignment = WD_TABLE_ALIGNMENT.CENTER
    s_headers = ["Collection Path", "Field", "Description / Constraints"]
    for c_idx, h in enumerate(s_headers):
        cell = tbl_schema.cell(0, c_idx)
        set_cell_background(cell, "1F242E")
        set_cell_margins(cell, top=100, bottom=100, left=100, right=100)
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(h)
        r.font.bold = True
        r.font.size = Pt(9.0)
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    schema_data = [
        ("users/{uid}/chats/{chatId}", "title, createdAt, updatedAt, messageCount, toolRuns", "Stores metadata for an individual chat session. Updated atomically on new message."),
        ("users/{uid}/chats/{chatId}/messages/{msgId}", "role, content, toolUsed, toolResult, timestamp", "Subcollection of messages. Role is 'user' or 'assistant'. Includes structured toolResult payload."),
    ]
    for r_idx, (path, fields, desc) in enumerate(schema_data, start=1):
        bg = "FFFFFF" if r_idx % 2 != 0 else "F8F9FA"
        for c_idx, val in enumerate([path, fields, desc]):
            cell = tbl_schema.cell(r_idx, c_idx)
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=80, bottom=80, left=80, right=80)
            set_cell_border(cell, top="single", bottom="single", top_color="E0E0E0", bottom_color="E0E0E0")
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            r = p.add_run(val)
            r.font.size = Pt(8.5)

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # =========================================================================
    # SECTION 5: FRONTEND ARCHITECTURE (REACT 18 + VITE)
    # =========================================================================
    add_h1("5. Frontend Architecture & State Management")

    doc.add_paragraph(
        "The frontend is implemented with React 18 and Vite. It is structured around custom React hooks "
        "that encapsulate authentication, chat sessions, and asynchronous stream handling."
    )

    add_h2("5.1 Core Custom Hooks")
    hooks_info = [
        ("useAuth.js", "Manages user lifecycle (login, registration, Google popup authentication, token refresh, and signout) via onAuthStateChanged listeners."),
        ("useChats.js", "Subscribes to Firestore chat collections in real-time, handling session creation, switching, renaming, and soft-deletes."),
        ("useStreamingChat.js", "State machine handling the SSE stream. Manages active tool results, streaming chunk accumulation, error boundaries, and auto-scrolling."),
    ]
    for name, desc in hooks_info:
        p = doc.add_paragraph(style='List Bullet')
        r = p.add_run(f"{name}: ")
        r.font.bold = True
        p.add_run(desc)

    add_h2("5.2 Component Hierarchy")
    add_code_block("""App.jsx
 ├── Login.jsx (Authentication Guard & OAuth)
 └── Chat.jsx (Main Workspace Shell)
      ├── Sidebar.jsx (Chat History, New Chat, Session Management)
      ├── ChatWindow.jsx (Message Stream Container)
      │    ├── WelcomeCapsules.jsx (Suggested Prompts & Tool Shortcuts)
      │    ├── MessageBubble.jsx (User / Assistant Bubble)
      │    │    └── ToolResultBubble.jsx (Structured Cards: Confidence & Chips)
      │    └── CommentaryStream.jsx (Real-time Markdown Streaming Indicator)
      └── ToolSelector.jsx (Interactive NLP Tool Dropdown & Input Modals)""")

    # =========================================================================
    # SECTION 6: COMPLETE API SPECIFICATION
    # =========================================================================
    add_h1("6. API Endpoints Reference")

    add_h2("6.1 GET /health")
    doc.add_paragraph("Confirms backend availability and verifies that all 5 fine-tuned models are resident in memory.")
    add_code_block("""// Response (200 OK)
{
  "status": "ok",
  "tools_loaded": ["sentiment", "topic", "ner", "summarization", "qa"]
}""")

    add_h2("6.2 GET /tools")
    doc.add_paragraph("Returns JSON Schema descriptors for all registered NLP tools, allowing the frontend to dynamically render tool parameters and input constraints.")
    add_code_block("""// Response (200 OK)
{
  "tools": [
    {
      "id": "sentiment",
      "display_name": "Sentiment Analyzer",
      "description": "Tells you whether a piece of text is positive or negative.",
      "base_model": "DistilBERT",
      "fine_tune_dataset": "SST-2",
      "input_schema": {
        "type": "object",
        "required": ["text"],
        "properties": {
          "text": {"type": "string", "maxLength": 5000}
        }
      }
    }
  ]
}""")

    add_h2("6.3 POST /chat (SSE Stream)")
    doc.add_paragraph("Primary conversational and tool execution endpoint. Requires a valid Firebase JWT in the Authorization header.")
    add_code_block("""// Request Payload
{
  "chatId": "chat_abc123",
  "message": "Analyze the sentiment of this review: The system operates flawlessly!",
  "toolId": "sentiment",
  "toolInput": {
    "text": "The system operates flawlessly!"
  }
}""")

    # =========================================================================
    # SECTION 7: DEPLOYMENT & TROUBLESHOOTING
    # =========================================================================
    add_h1("7. Operational Diagnostics & Model Downloader")

    doc.add_paragraph(
        "TextSphere includes automated command-line utilities to simplify environment provisioning and verification."
    )

    p_cmd1 = doc.add_paragraph(style='List Bullet')
    r = p_cmd1.add_run("Automated Model Downloader (download_models.py): ")
    r.font.bold = True
    p_cmd1.add_run("Directly synchronizes pre-trained model weights from Google Drive using gdown and automatically formats Safetensors checkpoint files.")

    p_cmd2 = doc.add_paragraph(style='List Bullet')
    r = p_cmd2.add_run("Environment Verifier (setup_check.py): ")
    r.font.bold = True
    p_cmd2.add_run("Pre-flight validation script checking model files, Firebase credentials JSON, environment variables (.env), and Python dependencies before launching servers.")

    # Save document
    output_path = "TextSphere_Developer_Documentation.docx"
    doc.save(output_path)
    print(f"Successfully generated: {output_path}")


if __name__ == "__main__":
    build_documentation()
