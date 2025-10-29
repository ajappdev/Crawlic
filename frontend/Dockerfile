# ========= STAGE 1: BUILD (Vite 7 + Node 20) =========
FROM node:20-alpine AS builder

WORKDIR /app

# Cache deps
COPY package*.json ./
RUN npm ci

# Copy source
COPY . .

# Production build (creates /app/dist)
ENV NODE_ENV=production
RUN npm run build


# ========= STAGE 2: SERVE WITH NGINX =========
FROM nginx:alpine

# Copy built assets
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy custom config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# ------------------------------------------------------------------
#  FIX: create all Nginx temp directories and give the nginx user
#       write permission BEFORE switching to that user.
# ------------------------------------------------------------------
RUN mkdir -p \
        /var/cache/nginx/client_temp \
        /var/cache/nginx/proxy_temp \
        /var/cache/nginx/fastcgi_temp \
        /var/cache/nginx/uwsgi_temp \
        /var/cache/nginx/scgi_temp \
    && chown -R nginx:nginx /var/cache/nginx \
    && chown -R nginx:nginx /var/log/nginx \
    && chown -R nginx:nginx /etc/nginx/conf.d

# Run as non-root
USER nginx

# Health-check endpoint (make sure you have /health in nginx.conf)
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget -qO- http://localhost/health >/dev/null 2>&1 || exit 1

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]