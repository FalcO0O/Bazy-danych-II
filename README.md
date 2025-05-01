# Databases II – Auction Web App

This project is an **auction website** powered by a **MongoDB** database. The backend technology is yet to be decided.

## 🐳 Docker Setup

The project uses **Docker** to run both the web application and the MongoDB database.

### Getting Started

1. Navigate to the main project directory:

   ```sh
   cd BAZY-DANYCH-II
   ```

2. Run the app using Docker Compose:

   ```sh
   docker compose up
   ```

This will start both the backend (when added) and the MongoDB container.

## 🍃 MongoDB Configuration

The MongoDB database is set up inside a Docker container and is accessible at:

```
mongodb://localhost:27017
```

> ⚠️ **Note:** Authentication is currently **disabled**, so you don't need to provide a username or password to connect.