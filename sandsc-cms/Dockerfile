FROM node:20

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

ENV NODE_ENV=production

EXPOSE 1337

CMD ["npm", "run", "start"]
