FROM texlive/texlive:latest

# Install Python and Flask
RUN apt-get update && apt-get install -y python3 python3-pip
RUN pip3 install --break-system-packages flask gunicorn

# Copy application
COPY app.py /app/app.py
WORKDIR /app

# Expose port
EXPOSE 10000

# Run with gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:10000", "-w", "2", "--timeout", "120", "app:app"]
