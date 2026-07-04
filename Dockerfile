# Nischay runs on the Python standard library alone — this image needs nothing
# but Python itself. Any host that runs a container can serve it.
FROM python:3.11-slim
WORKDIR /app
COPY . .
# Bind all interfaces (a container is isolated anyway); a host that injects its
# own $PORT is honoured automatically by app.py.
ENV HOST=0.0.0.0 \
    PORT=8000 \
    NO_BROWSER=1
EXPOSE 8000
CMD ["python3", "app.py"]
