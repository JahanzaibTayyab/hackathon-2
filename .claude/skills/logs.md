# Show Application Logs Skill

Display recent logs from both frontend and backend servers.

## Usage
```bash
/logs
```

## What it does
1. Shows last 50 lines of backend logs
2. Shows last 50 lines of frontend logs
3. Highlights errors and warnings
4. Shows current server status

## Commands
```bash
# Check backend logs
tail -50 /tmp/claude/-Users-zaib-Panaverse-hackathon-2/tasks/b0cdd87.output

# Check frontend logs
tail -50 /tmp/claude/-Users-zaib-Panaverse-hackathon-2/tasks/b575a22.output

# Check server status
curl -s http://localhost:8000/health
curl -s http://localhost:3000 > /dev/null && echo "Frontend: Running" || echo "Frontend: Not responding"
```

## Success Criteria
- Logs are displayed successfully
- Server status is shown
- Any errors are highlighted
