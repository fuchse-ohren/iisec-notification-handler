FROM python:3

WORKDIR /usr/src/app

COPY ./* ./
RUN pip install -r ./requirements.txt

RUN mkdir /usr/src/app/model
WORKDIR /usr/src/app/model
RUN wget -O "gemma-2-2b-jpn-it-Q2_K.gguf" "https://huggingface.co/tensorblock/gemma-2-2b-jpn-it-GGUF/resolve/main/gemma-2-2b-jpn-it-Q2_K.gguf?download=true"

WORKDIR /usr/src/app
CMD [ "python", "daemon.py" ]
