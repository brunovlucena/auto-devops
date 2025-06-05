FROM node:18-alpine

WORKDIR /app

COPY package.json .
COPY index.js .
COPY {{.ParserId}}.js .

RUN npm install

ENV NODE_PATH=/app/node_modules

ENTRYPOINT ["npm", "start"] 