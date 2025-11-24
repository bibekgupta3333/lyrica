# Database Viewers Guide

## Overview

Lyrica includes two powerful database management tools for local development:

- **pgAdmin**: Full-featured PostgreSQL web interface
- **Redis Commander**: Lightweight Redis management tool

Both run in Docker containers and are accessible via your web browser.

---

## 🐘 pgAdmin (PostgreSQL Web UI)

### Access Information

- **URL**: http://localhost:5050
- **Email**: admin@admin.com
- **Password**: admin
- **Port**: 5050

### Initial Setup

1. Open http://localhost:5050 in your browser
2. Log in with the credentials above
3. Click **"Add New Server"** in the Dashboard
4. Fill in the connection details:

   **General Tab:**
   - Name: `Lyrica DB`

   **Connection Tab:**
   - Host name/address: `postgres` (or `localhost` if not working)
   - Port: `5432`
   - Maintenance database: `lyrica_dev`
   - Username: `postgres`
   - Password: `postgres`

5. Click **Save**

### Features

✅ **Database Browser**
- Navigate through databases, schemas, tables, and columns
- View table data with filtering and sorting
- Visual representation of database structure

✅ **Query Tool**
- SQL editor with syntax highlighting
- Execute queries and view results
- Export query results (CSV, JSON, etc.)
- Query history

✅ **Table Management**
- Create, modify, and delete tables
- Add/remove columns
- Set constraints and indexes
- View table properties and statistics

✅ **Import/Export**
- Import data from CSV, Excel, JSON
- Export tables and query results
- Backup and restore databases

✅ **Performance Monitoring**
- View active queries
- Monitor database connections
- Check database statistics
- Analyze query performance

### Common Tasks

#### View All Tables
1. Expand: **Servers** → **Lyrica DB** → **Databases** → **lyrica_dev** → **Schemas** → **public** → **Tables**
2. Right-click any table → **View/Edit Data** → **All Rows**

#### Run a SQL Query
1. Right-click **lyrica_dev** → **Query Tool**
2. Enter your SQL:
   ```sql
   SELECT * FROM users LIMIT 10;
   ```
3. Press **F5** or click the ▶️ button

#### Export Table Data
1. Right-click table → **Import/Export**
2. Toggle **Export** switch
3. Choose format (CSV, JSON, etc.)
4. Click **OK**

---

## 🔴 Redis Commander (Redis Web UI)

### Access Information

- **URL**: http://localhost:8082
- **Port**: 8082
- **Auto-connects to**: Redis on port 6379

### Features

✅ **Key Browser**
- View all Redis keys organized by database
- Search keys by pattern
- Tree view for namespaced keys

✅ **Data Viewer**
- View and edit key values
- Supports all Redis data types:
  - Strings
  - Lists
  - Sets
  - Sorted Sets
  - Hashes

✅ **Key Management**
- Add/delete keys
- Set expiration (TTL)
- Rename keys
- Copy key values

✅ **Redis CLI**
- Execute raw Redis commands
- View command results
- Command history

✅ **Monitoring**
- View Redis info and statistics
- Monitor memory usage
- Check key count per database

### Common Tasks

#### View All Keys
1. Open http://localhost:8082
2. Keys are listed in the left sidebar
3. Click any key to view its value

#### Search for Keys
1. Use the search box at the top
2. Supports patterns:
   - `user:*` - all keys starting with "user:"
   - `*cache*` - all keys containing "cache"
   - `session:*:token` - namespaced keys

#### Add a New Key
1. Click **Add Key** button
2. Enter key name
3. Select data type
4. Enter value
5. Optionally set TTL (expiration)
6. Click **Save**

#### Execute Redis Commands
1. Click **CLI** in the top menu
2. Enter command (e.g., `INFO`, `KEYS *`, `GET mykey`)
3. Press **Enter**

---

## 🎛️ Service Management

### Start Services

```bash
# Start all Docker services (including viewers)
pnpm docker:up

# Or using docker-compose directly
docker-compose up -d
```

### Stop Services

```bash
# Stop all services
pnpm docker:down

# Or stop specific service
docker stop lyrica-pgadmin
docker stop lyrica-redis-commander
```

### View Logs

```bash
# All services
pnpm docker:logs

# Specific service
docker logs -f lyrica-pgadmin
docker logs -f lyrica-redis-commander
```

### Restart a Service

```bash
# Restart pgAdmin
docker restart lyrica-pgadmin

# Restart Redis Commander
docker restart lyrica-redis-commander
```

---

## 🔧 Troubleshooting

### pgAdmin Won't Start

**Problem**: Container keeps restarting

**Solution 1**: Check logs
```bash
docker logs lyrica-pgadmin
```

**Solution 2**: Reset pgAdmin data
```bash
docker-compose down
docker volume rm lyrica_pgadmin_data
pnpm docker:up
```

### Can't Connect to PostgreSQL in pgAdmin

**Problem**: "could not connect to server"

**Solution**: Use `postgres` as hostname (not `localhost`)
- Docker containers use the service name for DNS
- If that doesn't work, try `host.docker.internal` on Mac/Windows

### Redis Commander Shows No Keys

**Problem**: Dashboard is empty

**Reason**: Redis is probably empty (no data yet)

**Test**: Add a test key via CLI
```bash
docker exec -it lyrica-redis redis-cli
> SET test "Hello"
> GET test
> KEYS *
```

### Port Already in Use

**Problem**: "port 5050 already in use" or "port 8082 already in use"

**Solution 1**: Kill processes on those ports
```bash
# Kill pgAdmin port
lsof -ti:5050 | xargs kill -9

# Kill Redis Commander port
lsof -ti:8082 | xargs kill -9
```

**Solution 2**: Change ports in docker-compose.yml
```yaml
pgadmin:
  ports:
    - "5051:80"  # Use 5051 instead of 5050

redis-commander:
  ports:
    - "8083:8081"  # Use 8083 instead of 8082
```

---

## 🔒 Security Notes

⚠️ **IMPORTANT**: These tools are configured for **DEVELOPMENT ONLY**

### Development Settings (Current)
- Simple passwords (`admin`)
- No SSL/TLS encryption
- Exposed ports on `0.0.0.0` (all interfaces)
- No authentication restrictions

### Production Recommendations
❌ **DO NOT** use these tools in production
❌ **DO NOT** expose ports 5050 and 8082 publicly
❌ **DO NOT** use default passwords

If you need database access in production:
✅ Use SSH tunneling
✅ Use VPN for secure access
✅ Use strong, unique passwords
✅ Enable SSL/TLS
✅ Implement IP whitelisting
✅ Use read-only credentials when possible

---

## 🎯 Alternatives

### Other PostgreSQL Clients
- **DBeaver**: Free, cross-platform, supports many databases
- **TablePlus**: Beautiful native macOS client
- **DataGrip**: JetBrains IDE, very powerful
- **Postico**: macOS PostgreSQL client
- **psql**: Command-line client (included with PostgreSQL)

### Other Redis Clients
- **RedisInsight**: Official Redis GUI (feature-rich)
- **Medis**: macOS Redis client
- **Redis Desktop Manager**: Cross-platform
- **redis-cli**: Command-line client (included with Redis)

### Code-Based Admin Panels
These require integration into your FastAPI app:
- **SQLAlchemy Admin**: Admin panel for SQLAlchemy models
- **FastAPI Admin**: FastAPI-specific admin framework
- **Piccolo Admin**: Python admin interface

---

## 📚 Resources

### pgAdmin
- [Official Documentation](https://www.pgadmin.org/docs/)
- [Query Tool Guide](https://www.pgadmin.org/docs/pgadmin4/latest/query_tool.html)
- [pgAdmin Docker Image](https://hub.docker.com/r/dpage/pgadmin4/)

### Redis Commander
- [GitHub Repository](https://github.com/joeferner/redis-commander)
- [Docker Image](https://hub.docker.com/r/rediscommander/redis-commander)

### PostgreSQL
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [SQL Tutorial](https://www.postgresql.org/docs/current/tutorial.html)

### Redis
- [Redis Commands](https://redis.io/commands)
- [Redis Documentation](https://redis.io/documentation)
- [Try Redis Interactive Tutorial](https://try.redis.io/)

---

## 🎓 Learning Path

If you're new to these databases:

### PostgreSQL Basics
1. Learn SQL fundamentals (SELECT, INSERT, UPDATE, DELETE)
2. Understand relationships (foreign keys, joins)
3. Practice with pgAdmin Query Tool
4. Learn about indexes and performance

### Redis Basics
1. Understand key-value storage
2. Learn Redis data types
3. Practice with Redis Commander CLI
4. Learn about TTL and expiration
5. Understand caching strategies

---

## ✅ Quick Reference

### Service URLs
```
Backend API:       http://localhost:8000
API Docs:          http://localhost:8000/docs
pgAdmin:           http://localhost:5050
Redis Commander:   http://localhost:8082
ChromaDB:          http://localhost:8001
```

### Database Connections
```
PostgreSQL:  localhost:5432 / lyrica_dev / postgres / postgres
Redis:       localhost:6379
ChromaDB:    localhost:8001
```

### Common Commands
```bash
# Start all services
pnpm docker:up

# View running services
docker ps

# View logs
pnpm docker:logs

# Stop all services
pnpm docker:down

# Restart everything
pnpm restart
```

---

**Happy debugging! 🐛🔍**
