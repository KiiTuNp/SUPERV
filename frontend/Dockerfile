FROM node:20-alpine AS builder

WORKDIR /app

# Copy package.json first for better caching
COPY package.json ./

# Copy yarn.lock if it exists, otherwise skip
COPY yarn.loc[k] ./

# Clean install dependencies
RUN yarn install --network-timeout 1000000 --frozen-lockfile || yarn install --network-timeout 1000000

# Copy source code
COPY . .

# Build the app
RUN yarn build

# Production stage
FROM nginx:alpine

# Copy custom nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built app from builder stage
COPY --from=builder /app/build /usr/share/nginx/html

# Create healthcheck endpoint
RUN echo "healthy" > /usr/share/nginx/html/health

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:3000/health || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]