FROM python:3.11
RUN pip install fastapi uvicorn pymongo pydantic
COPY ./app /app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000" ]
