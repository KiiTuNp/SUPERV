# SUPER Vote Secret Frontend - Production Optimized Dockerfile
# Multi-stage build for minimal production image

# Build stage
FROM node:20-alpine as builder

# Build arguments
ARG BUILDKIT_INLINE_CACHE=1
ARG NODE_ENV=production
ARG REACT_APP_BACKEND_URL

# Install build dependencies
RUN apk add --no-cache \
    python3 \
    make \
    g++ \
    && rm -rf /var/cache/apk/*

# Set working directory
WORKDIR /app

# Copy package files
COPY package.json yarn.lock ./

# Install dependencies with optimal caching
RUN yarn install --frozen-lockfile --production=false --network-timeout 100000

# Copy source code
COPY . .

# Build application
ENV NODE_ENV=production
ENV GENERATE_SOURCEMAP=false
ENV REACT_APP_BACKEND_URL=$REACT_APP_BACKEND_URL

RUN yarn build

# Production stage
FROM nginx:1.25-alpine as production

# Install runtime dependencies
RUN apk add --no-cache \
    curl \
    && rm -rf /var/cache/apk/*

# Remove default nginx content
RUN rm -rf /usr/share/nginx/html/*

# Copy built application
COPY --from=builder /app/build /usr/share/nginx/html

# Copy optimized nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Create nginx user and set permissions
RUN addgroup -g 101 -S nginx && \
    adduser -S -D -H -u 101 -h /var/cache/nginx -s /sbin/nologin -G nginx -g nginx nginx && \
    chown -R nginx:nginx /usr/share/nginx/html && \
    chown -R nginx:nginx /var/cache/nginx && \
    chmod -R 755 /usr/share/nginx/html

# Create health check endpoint
RUN echo 'healthy' > /usr/share/nginx/html/health

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:3000/health || exit 1

# Expose port
EXPOSE 3000

# Switch to non-root user
USER nginx

# Start nginx
CMD ["nginx", "-g", "daemon off;"]