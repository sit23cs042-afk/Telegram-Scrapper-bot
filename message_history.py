"""
Message History Manager
Tracks last processed message and catches up on missed messages
"""
import os
import json
from datetime import datetime, timedelta
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
        """Get last processed time for a channel"""
        channel_key = str(channel).lower()
        if channel_key in self.data:
            timestamp = self.data[channel_key]
            return datetime.fromisoformat(timestamp)
        # Default: 24 hours ago (for first run)
        return datetime.now() - timedelta(hours=24)
    
    def update_last_processed(self, channel, message_date):
        """Update last processed time for a channel"""
        channel_key = str(channel).lower()
        self.data[channel_key] = message_date.isoformat()
        self._save()
    
    def get_catchup_period_hours(self):
        """Get how many hours to catch up (configurable)"""
        return int(os.getenv('CATCHUP_HOURS', 24))  # Default 24 hours
