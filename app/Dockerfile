FROM python:3.9.2

EXPOSE 8501

WORKDIR /app
COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install streamlit
RUN pip install -r requirements.txt

ENTRYPOINT [ "streamlit", "run"]
CMD ["/app.py"]
