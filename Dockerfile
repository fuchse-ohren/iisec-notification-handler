FROM python:3

WORKDIR /usr/src/app

COPY ./* ./
RUN pip install -r ./requirements.txt

RUN mkdir /usr/src/app/model
WORKDIR /usr/src/app/model
RUN wget -O "tinyswallow-1.5b-instruct-q8_0.gguf" "https://huggingface.co/SakanaAI/TinySwallow-1.5B-Instruct-GGUF/resolve/main/tinyswallow-1.5b-instruct-q8_0.gguf?download=true"

WORKDIR /usr/src/app
CMD [ "python", "daemon.py" ]
