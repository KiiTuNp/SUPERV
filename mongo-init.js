// MongoDB initialization script for Vote Secret
db = db.getSiblingDB(process.env.MONGO_INITDB_DATABASE || 'vote_secret');

// Create collections with validation
db.createCollection('meetings');
db.createCollection('participants');
db.createCollection('polls');
db.createCollection('votes');
db.createCollection('scrutators');
db.createCollection('scrutator_access');

// Create indexes for better performance
db.meetings.createIndex({ "meeting_code": 1 }, { unique: true });
db.meetings.createIndex({ "created_at": 1 });
db.meetings.createIndex({ "status": 1 });

db.participants.createIndex({ "meeting_id": 1 });
db.participants.createIndex({ "meeting_id": 1, "name": 1 }, { unique: true });

db.polls.createIndex({ "meeting_id": 1 });
db.polls.createIndex({ "status": 1 });

db.votes.createIndex({ "poll_id": 1 });
db.votes.createIndex({ "participant_id": 1 });

db.scrutators.createIndex({ "meeting_id": 1 });
db.scrutators.createIndex({ "meeting_id": 1, "name": 1 }, { unique: true });

print('✅ Vote Secret database initialized successfully');
print('📊 Collections created: meetings, participants, polls, votes, scrutators, scrutator_access');
print('🔍 Indexes created for optimal performance');