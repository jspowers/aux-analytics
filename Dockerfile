FROM python:3.9.2-slim

EXPOSE 8501

WORKDIR /aux-analytics
COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install streamlit
RUN pip install -r requirements.txt

COPY ./app /streamlit_test
ENTRYPOINT ["streamlit", "run"]
CMD ["/streamlit_test/test.py"]
