# ========= STAGE 1: BUILD =========
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
ENV NODE_ENV=production
RUN npm run build

# ========= STAGE 2: SERVE =========
FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Create PID dir
RUN mkdir -p /run/nginx && chown nginx:nginx /run/nginx

# Remove USER nginx
# Let entrypoint run as root, then drop

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget -qO- http://localhost/health >/dev/null 2>&1 || exit 1

EXPOSE 80

# Start as root, drop to nginx user
CMD ["nginx", "-g", "daemon off; user nginx;"]