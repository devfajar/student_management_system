# Stage 1: Build production bundle using Bun
FROM oven/bun:1-alpine AS builder

WORKDIR /app

# Cache package dependencies
COPY package.json bun.lock* ./
RUN bun install --frozen-lockfile || bun install

# Copy application source code
COPY . .

# Build production distribution
RUN bun run build

# Stage 2: Lightweight Nginx Alpine server
FROM nginx:alpine

# Copy built web assets to nginx document root
COPY --from=builder /app/dist /usr/share/nginx/html

# Replace default Nginx configuration with reverse-proxy SPA configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
