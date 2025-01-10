FROM python:3.12-slim

# Copy files
COPY ./src /home/ui/

RUN apt-get update && apt-get install -y curl && \
    groupadd --gid 2000 ui && \
    useradd --uid 2000 --gid ui \
            --home /home/ui \
            --create-home \
            --shell /bin/bash ui && \
    pip install streamlit streamlit-extras && \
    chown ui:ui -R /home/ui

WORKDIR /home/ui

USER ui:ui

EXPOSE 80

HEALTHCHECK CMD curl --fail http://localhost:80/_stcore/health

CMD streamlit run chat.py --server.port=80 --server.address=0.0.0.0