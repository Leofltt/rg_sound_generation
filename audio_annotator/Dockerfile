FROM python:3.8-buster
ENV PYTHONUNBUFFERED True
ENV APP_HOME /app
ENV PORT 80
RUN apt update -y
RUN apt-get install libsndfile1 -y
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
RUN wget https://osr-tsoai.s3.amazonaws.com/guitar_pitch_60_audio.zip
RUN unzip -o guitar_pitch_60_audio.zip -d ./audio_annotator/static
ENV FLASK_APP audio_annotator
ENV FLASK_ENV development
ENV FLASK_HOST_IP 0.0.0.0
RUN flask build-db
RUN flask generate-spectrograms
RUN flask load-pre-db
EXPOSE 80
CMD exec waitress-serve --port $PORT --call "audio_annotator:create_app"
