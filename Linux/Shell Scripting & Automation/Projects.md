### 5. Projects

#### Project 1: Backup Automation Script
**Goal**: Create a script to back up a directory to a remote server and log the process.

```x-shellscript
#!/bin/bash

# Backup script for /home/user/docs
SOURCE="/home/user/docs"
DEST="user@remote:/backups"
LOG="/var/log/backup.log"

# Trap Ctrl+C to log interruption
trap 'echo "$(date): Backup interrupted!" >> $LOG; exit 1' SIGINT

# Check if source directory exists
if [ ! -d "$SOURCE" ]; then
  echo "$(date): Error: Source $SOURCE does not exist." >> $LOG
  exit 1
fi

# Perform backup with rsync
rsync -avz --delete "$SOURCE/" "$DEST" >> "$LOG" 2>&1
if [ $? -eq 0 ]; then
  echo "$(date): Backup completed successfully." >> "$LOG"
else
  echo "$(date): Backup failed!" >> "$LOG"
  exit 1
fi
```

**How to Use**:
1. Save as `backup.sh`, make executable: `chmod +x backup.sh`.
2. Schedule with cron: `crontab -e`, add `0 1 * * * /path/to/backup.sh`.
3. **Use Case**: Automatically back up critical files nightly.

#### Project 2: Log Monitoring Alert Script
**Goal**: Monitor a log file for errors and send an email alert.

```x-shellscript
#!/bin/bash

# Monitor /var/log/syslog for errors
LOG="/var/log/syslog"
EMAIL="admin@example.com"
TEMP="/tmp/error.log"

# Check last 100 lines for "error"
tail -n 100 "$LOG" | grep -i "error" > "$TEMP"
if [ -s "$TEMP" ]; then
  # Send alert if errors found
  mail -s "Errors detected in $LOG" "$EMAIL" < "$TEMP"
  echo "$(date): Errors found, alert sent." >> /var/log/monitor.log
else
  echo "$(date): No errors found." >> /var/log/monitor.log
fi

# Clean up
rm -f "$TEMP"
```

**How to Use**:
1. Save as `monitor.sh`, make executable: `chmod +x monitor.sh`.
2. Install mailutils: `sudo apt install mailutils`.
3. Schedule with cron: `*/5 * * * * /path/to/monitor.sh` (every 5 minutes).
4. **Use Case**: Monitor server logs for issues and notify admins.

#### Project 3: Weather Notifier Using `curl` and APIs
**Goal**: Fetch weather data from an API and display it.

```x-shellscript
#!/bin/bash

# Fetch weather for a city using OpenWeatherMap API
CITY="London"
API_KEY="your_api_key_here"
URL="http://api.openweathermap.org/data/2.5/weather?q=$CITY&appid=$API_KEY&units=metric"

# Get weather data
DATA=$(curl -s "$URL")
if [ $? -ne 0 ]; then
  echo "Error fetching weather data."
  exit 1
fi

# Extract temperature and description
TEMP=$(echo "$DATA" | grep -oP '"temp":\d+\.\d+' | cut -d: -f2)
DESC=$(echo "$DATA" | grep -oP '"description":"[^"]+"' | cut -d: -f2 | tr -d '"')

# Display result
echo "Weather in $CITY: $TEMP°C, $DESC"
```

**How to Use**:
1. Sign up at `openweathermap.org` to get an API key.
2. Replace `your_api_key_here` with your key.
3. Save as `weather.sh`, make executable: `chmod +x weather.sh`.
4. Run: `./weather.sh`.
5. Schedule with cron: `0 8 * * * /path/to/weather.sh >> /var/log/weather.log`.
6. **Use Case**: Display daily weather updates or log them.

---
