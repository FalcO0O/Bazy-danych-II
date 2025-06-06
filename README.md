# Auctions API - DataBases 2

This project is a backend service for an auction platform built using **FastAPI** and **MongoDB**. It provides endpoints for user registration, authentication with JWT tokens, auction creation, bidding, and role-based access control.

The system is designed with **asynchronous operations** and **supports transactional updates** where needed to ensure data consistency.

## 🐳 Docker Setup

This project uses **Docker** to run the backend and manage all API endpoints. The database is hosted externally via **MongoDB Atlas**, but you can switch to a local instance if preferred.

The `docker-compose.yml` includes a commented section for spinning up a local MongoDB container — simply uncomment it to switch from Atlas to local setup.

### Environment Setup

1. In the main project directory, create a `.env` file:

   ```sh
   cd BAZY-DANYCH-II
   ```

2. Add the following variables to the `.env` file:

   ```env
   SECRET_KEY=your_secret_key_here

   ACCESS_TOKEN_EXPIRE_MINUTES=30
   REFRESH_TOKEN_EXPIRE_MINUTES=10080

   DB_NAME=your_database_name
   MONGO_URL=your_database_url
   ```

3. Example `.env` using a local MongoDB setup:

   ```env
   SECRET_KEY=abcdefg1234567

   ACCESS_TOKEN_EXPIRE_MINUTES=30
   REFRESH_TOKEN_EXPIRE_MINUTES=10080

   DB_NAME=AuctionDB
   MONGO_URL=mongodb://localhost:27017
   ```

### Running with Docker

1. Navigate to the root of the project:

   ```sh
   cd BAZY-DANYCH-II
   ```

2. Start the services with Docker Compose:

   ```sh
   docker compose up
   ```

This will launch the FastAPI backend (when added) and optionally the MongoDB container, depending on your configuration.

### Testing the API

To test API, use attached postman collection
`Auction-API.postman_collection.json`

### 📄 API Documentation

FastAPI automatically provides interactive API docs:

- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)  
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

Docs are auto-generated based on route definitions and Python docstrings.