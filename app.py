from flask import Flask, request, send_file, jsonify
import subprocess
import tempfile
import os
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "service": "latex-compiler"})

@app.route('/compile', methods=['POST'])
def compile_latex():
    try:
        # Get LaTeX code from request body
        latex_code = request.data.decode('utf-8')
        
        if not latex_code:
            return jsonify({"error": "No LaTeX code provided"}), 400
        
        # Create temporary directory
        with tempfile.TemporaryDirectory() as tmpdir:
            tex_file = os.path.join(tmpdir, 'document.tex')
            pdf_file = os.path.join(tmpdir, 'document.pdf')
            
            # Write LaTeX code to file
            with open(tex_file, 'w', encoding='utf-8') as f:
                f.write(latex_code)
            
            # Compile with pdflatex (run twice for references)
            for i in range(2):
                result = subprocess.run(
                    ['pdflatex', '-interaction=nonstopmode', '-halt-on-error', 'document.tex'],
                    cwd=tmpdir,
                    capture_output=True,
                    timeout=60
                )
            
            # Check if PDF was created
            if os.path.exists(pdf_file):
                return send_file(
                    pdf_file,
                    mimetype='application/pdf',
                    as_attachment=True,
                    download_name='document.pdf'
                )
            else:
                # Return compilation errors
                error_log = result.stderr.decode('utf-8', errors='ignore')
                logging.error(f"LaTeX compilation failed: {error_log}")
                return jsonify({
                    "error": "LaTeX compilation failed",
                    "details": error_log[:1000]  # First 1000 chars
                }), 500
                
    except subprocess.TimeoutExpired:
        return jsonify({"error": "Compilation timeout (>60s)"}), 500
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
