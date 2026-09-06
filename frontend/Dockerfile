# ============================================================================
# Stage 1: Build React/TypeScript application with Vite
# ============================================================================
FROM node:18-alpine as build-stage

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci

# Copy source code and build production distribution
COPY . .
RUN npm run build

# ============================================================================
# Stage 2: Serve production bundle with Nginx
# ============================================================================
FROM nginx:alpine as production-stage

# Copy built assets
COPY --from=build-stage /app/dist /usr/share/nginx/html

# Copy custom Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
