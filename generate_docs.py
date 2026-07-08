import os
from markdown_pdf import MarkdownPdf
from markdown_pdf import Section

doc_content = """
# Cloud-Based AI Python Code Generator & Live Preview Platform
**MCA Final Year Project - Specialization: Cloud Computing**
**Author:** Vaibhav

---

## 1. Project Overview
This project is a comprehensive cloud-native platform that allows users to generate Python code using Artificial Intelligence (Google Gemini), edit that code in a web-based Monaco editor, and execute it securely in a real-time, sandboxed cloud environment. It also includes an advanced desktop terminal client for local execution and AI error fixing.

---

## 2. Directory Structure & File Explanations

### `frontend/` - Web Application
Built with **Next.js 14**, **React**, and **TailwindCSS**.
- `src/app/page.tsx`: The main user interface. It contains the layout for the AI prompt input, the code editor, and the Live Execution Terminal side-by-side. It manages the WebSocket connection to the backend for real-time code execution streaming.
- `src/components/editor/MonacoEditor.tsx`: Integrates the Microsoft Monaco Editor (the same editor powering VS Code) into the browser with Python syntax highlighting.
- `src/components/console/LivePreview.tsx`: The custom UI component for the Live Execution Terminal. It renders the stdout/stderr stream from the cloud backend in real-time and handles auto-scrolling to the bottom of the output.
- `src/lib/api-client.ts`: Handles HTTP requests to the backend for AI code generation and authentication.
- `src/lib/store.ts`: A Zustand state management store that synchronizes the generated code, execution status, and terminal output across all React components.

### `backend/` - Core API & Execution Engine
Built with **FastAPI**, following **Clean Architecture principles**.
- `app/presentation/routers/codegen_router.py`: Exposes the HTTP endpoint for generating Python code. It receives the user's prompt and forwards it to the domain layer.
- `app/presentation/routers/execution_router.py`: Manages the WebSocket (`/ws/interactive`) connections. It streams data back and forth between the frontend terminal and the execution backend.
- `app/domain/services/ai_code_service.py`: Contains the core business logic for communicating with the AI model to generate and refine Python code.
- `app/infrastructure/ai/gemini_client.py`: The low-level infrastructure adapter that talks directly to the Google Gemini API using the `google-generativeai` SDK.
- `app/infrastructure/execution/tasks.py`: Defines Celery asynchronous tasks for queueing and managing background code execution jobs.
- `app/infrastructure/execution/docker_executor.py`: (Crucial Component) securely spins up isolated, ephemeral Docker containers to run the user's Python code, capturing the input/output streams to prevent malicious code from harming the host server.

### `sandbox_image/` - Secure Execution Environment
- `Dockerfile`: Defines the blueprint for the secure execution container. It uses a lightweight Alpine Linux base (`python:3.12-alpine`), installs necessary standard libraries, and drops all root privileges to ensure malicious scripts cannot escape the container or access host resources.

### `terminal_ai/` - Desktop Terminal Client
A desktop companion app built with **Python & PySide6 (Qt)**.
- `main.py` & `ui.py`: Bootstraps the desktop GUI and handles the layout for the terminal interface.
- `terminal.py`: A custom QPlainTextEdit widget that intercepts keystrokes to behave exactly like a real terminal (blocking backspace on output, sending commands on Enter).
- `powershell.py`: Spawns a persistent, hidden `powershell.exe` process in the background. It uses multithreading to continuously stream stdout and stderr to the UI without freezing the application.
- `error_parser.py`: Continuously scans the terminal output using Regular Expressions to detect Python exceptions (e.g., `NameError`, `SyntaxError`).
- `ai_helper.py`: When an error is detected, this module automatically sends the traceback to the Google Gemini AI to retrieve a human-readable explanation and a suggested code fix.

### Root Infrastructure
- `docker-compose.yml`: The orchestration file. It spins up the entire cloud infrastructure locally, including the Frontend container, Backend API, Redis (for message brokering), PostgreSQL (for user data), and Celery worker nodes for scalable execution.
- `.env`: Stores sensitive environment variables such as the `GEMINI_API_KEY` and database credentials.

---

## 3. How the Code Execution Works (End-to-End)
1. **Trigger:** The user clicks "Run Code" on the frontend.
2. **WebSocket Connection:** `page.tsx` establishes a WebSocket connection to the backend `execution_router.py`.
3. **Container Provisioning:** The backend spins up an isolated `sandbox_image` Docker container specifically for this execution session.
4. **Streaming:** As the Python code executes inside the container, standard output (e.g., `print()` statements) and errors are streamed via the WebSocket back to the frontend.
5. **Interactive Input:** If the code asks for input (e.g., `input("Enter name:")`), the terminal pauses. The user types the input in the browser, which sends it through the WebSocket directly into the Docker container's standard input stream.
6. **Teardown:** Once the script finishes, the container is instantly destroyed to free up resources and ensure security.
"""

def generate_pdf():
    pdf = MarkdownPdf(toc_level=2)
    pdf.add_section(Section(doc_content))
    output_path = os.path.join("C:\\", "Users", "Vaibhav", "Desktop", "Ai_Python_Platform_Documentation.pdf")
    pdf.save(output_path)
    print(f"PDF successfully generated at: {output_path}")

if __name__ == "__main__":
    generate_pdf()
