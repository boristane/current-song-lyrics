FROM node:10.13

WORKDIR current-song-lyrics
COPY package*.json ./
COPY requirements.txt ./

RUN npm install

RUN apt-get update || : && apt-get install python python3-pip -y
RUN pip3 install -r requirements.txt

COPY . .

RUN npm run build
EXPOSE 5000
CMD [ "python", "./src/app.py" ]
