# frontend/Dockerfile
FROM node:18

WORKDIR /app
COPY . .
RUN npm install
RUN npm run build

# Serve built site using http-server
RUN npm install -g http-server
CMD ["http-server", "dist", "-p", "5173"]