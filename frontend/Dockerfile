# Frontend Dockerfile for CommitQuest Web
#
# Multi-stage build with development and production targets

# Base stage
FROM node:20-alpine as base

WORKDIR /app

# Development stage
FROM base as development

COPY package*.json ./
RUN npm ci

COPY . .

EXPOSE 3000

CMD ["npm", "start"]

# Build stage
FROM base as build

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine as production

# Security: Remove default nginx config
RUN rm /etc/nginx/conf.d/default.conf

# Copy custom nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built assets
COPY --from=build /app/build /usr/share/nginx/html

# Security: Run as non-root
RUN chown -R nginx:nginx /usr/share/nginx/html && \
    chmod -R 755 /usr/share/nginx/html

EXPOSE 80

# Security headers are configured in nginx.conf
CMD ["nginx", "-g", "daemon off;"]
