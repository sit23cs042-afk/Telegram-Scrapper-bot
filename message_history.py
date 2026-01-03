"""
Message History Manager
Tracks last processed message and last shutdown time
Only catches up when system was actually turned off
"""
import os
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

HISTORY_FILE = "last_processed.json"

class MessageHistoryManager:
    def __init__(self, history_file=HISTORY_FILE):
        self.history_file = history_file
        self.data = self._load()
    
    def _load(self):
        """Load last processed timestamps from file"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save(self):
        """Save last processed timestamps to file"""
        with open(self.history_file, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def get_last_processed_time(self, channel):
        """Get last processed time for a channel (timezone-aware)"""
        channel_key = str(channel).lower()
        if channel_key in self.data:
            timestamp = self.data[channel_key]
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            # Ensure timezone-aware
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        # Default: last shutdown time or 24 hours ago
        return self.get_last_shutdown_time()
    
    def update_last_processed(self, channel, message_date):
        """Update last processed time for a channel"""
        channel_key = str(channel).lower()
        # Ensure timezone-aware
        if message_date.tzinfo is None:
            message_date = message_date.replace(tzinfo=timezone.utc)
        self.data[channel_key] = message_date.isoformat()
        self._save()
    
    def get_last_shutdown_time(self):
        """Get when bot was last shut down"""
        if 'last_shutdown' in self.data:
            timestamp = self.data['last_shutdown']
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        # First run: 24 hours ago
        return datetime.now(timezone.utc) - timedelta(hours=24)
    
    def mark_shutdown(self):
        """Mark current time as shutdown time"""
        self.data['last_shutdown'] = datetime.now(timezone.utc).isoformat()
        self._save()
    
    def should_catch_up(self):
        """Check if we should catch up (only if bot was previously shut down)"""
        # If last_shutdown exists and is recent, we should catch up
        if 'last_shutdown' not in self.data:
            return True  # First run
        
        last_shutdown = self.get_last_shutdown_time()
        time_since_shutdown = datetime.now(timezone.utc) - last_shutdown
        
        # Catch up if shutdown was more than 5 minutes ago
        return time_since_shutdown.total_seconds() > 300
    
    def get_catchup_period_hours(self):
        """Get how many hours to catch up (configurable)"""
        return int(os.getenv('CATCHUP_HOURS', 24))  # Default 24 hours
