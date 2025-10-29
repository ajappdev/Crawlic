# ========= STAGE 1: BUILD (Vite 7 + Node 20) =========
FROM node:20-alpine AS builder

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install ALL dependencies (including devDependencies for build)
RUN npm ci

# Copy source code
COPY . .

# Build for production
ENV NODE_ENV=production
RUN npm run build

# ========= STAGE 2: SERVE WITH NGINX =========
FROM nginx:alpine

# Copy Vite's build output (dist/)
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy your custom nginx.conf
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Run as non-root user
USER nginx

# Healthcheck
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget -qO- http://localhost/health >/dev/null 2>&1 || exit 1

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]