FROM node:20-alpine

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm install

COPY . .

# Pass build arguments into the environment for Vite
ARG VITE_API_URL
ARG VITE_WS_URL
ENV VITE_API_URL=$VITE_API_URL
ENV VITE_WS_URL=$VITE_WS_URL

# Build the Vite project
RUN npm run build

# Install a simple static server
RUN npm install -g serve

# Serve the static files
CMD ["serve", "-s", "dist", "-l", "3000"]
