# How to Find Your Kolibri URL

## Quick Method

Run the finder script:

```bash
bash scripts/find-kolibri-url.sh
```

Or use Python:

```bash
python scripts/kolibri-find-server.py
```

## Manual Methods

### Method 1: Check Kolibri Status

```bash
# Check if Kolibri is running
kolibri status

# Get Kolibri configuration
kolibri manage showconfig
```

### Method 2: Check Default Port

Kolibri typically runs on port **8080**:

```bash
# Test if port 8080 is open
curl http://localhost:8080/api/content/channel

# Or check with Python
python scripts/kolibri-quick-test.py --kolibri-url http://localhost:8080
```

### Method 3: Check Kolibri Home Directory

```bash
# Find Kolibri home directory (usually ~/.kolibri)
ls ~/.kolibri/server/

# Check port file
cat ~/.kolibri/server/port
```

### Method 4: Check Running Processes

```bash
# On macOS/Linux
lsof -i :8080
# or
netstat -an | grep 8080

# On Windows
netstat -an | findstr 8080
```

### Method 5: Check Docker (if using Docker)

```bash
# List running containers
docker ps

# Check port mapping
docker ps | grep kolibri
```

## Common Kolibri URLs

- `http://localhost:8080` (most common)
- `http://localhost:8000`
- `http://127.0.0.1:8080`
- `http://0.0.0.0:8080`

## If Kolibri Isn't Running

### Start Kolibri

```bash
# Start Kolibri server
kolibri start

# Or with Docker
docker run -d -p 8080:8080 learningequality/kolibri
```

### Check Kolibri Logs

```bash
# View Kolibri logs
kolibri logs

# Or check log file
tail -f ~/.kolibri/logs/kolibri.log
```

## Testing the URL

Once you have a URL, test it:

```bash
python scripts/kolibri-quick-test.py --kolibri-url http://your-url:port
```

If it works, you'll see:
- ✅ Connected to Kolibri!
- List of available channels
- Number of videos

## Troubleshooting

### Connection Refused

- Kolibri might not be running: `kolibri start`
- Wrong port: Check with `kolibri manage showconfig`
- Firewall blocking: Check firewall settings

### Wrong Port

- Check Kolibri config: `kolibri manage showconfig`
- Check port file: `cat ~/.kolibri/server/port`
- Try common ports: 8080, 8000, 3000

### Kolibri Not Installed

```bash
# Install Kolibri
pip install kolibri

# Or use Docker
docker pull learningequality/kolibri
docker run -d -p 8080:8080 learningequality/kolibri
```
