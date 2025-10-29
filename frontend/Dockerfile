# frontend/Dockerfile (I provided this)
FROM node:18-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build  # ← Builds React app to /app/dist

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html  # ← Copies built files
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]