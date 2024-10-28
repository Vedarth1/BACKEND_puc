from src import mongo_db

class Counter:

    def __init__(self):
        # Initialize collection for counters
        self.counters_collection = mongo_db.counters

    def initialize_counters(self):
        # Initialize counters in MongoDB if they don't exist
        if self.counters_collection.count_documents({}) == 0:
            self.counters_collection.insert_one({"valid_puc_count": 0, "invalid_puc_count": 0})

    def increment_valid_puc_count(self):
        # Increment the count of valid PUCs by 1
        self.counters_collection.update_one({}, {'$inc': {'valid_puc_count': 1}}, upsert=True)

    def increment_invalid_puc_count(self):
        # Increment the count of invalid PUCs by 1
        self.counters_collection.update_one({}, {'$inc': {'invalid_puc_count': 1}}, upsert=True)

    def get_counts(self):
        # Retrieve current counts for valid and invalid PUCs
        counter_data = self.counters_collection.find_one({}, {"_id": 0})
        return {
            "valid_puc_count": counter_data.get("valid_puc_count", 0),
            "invalid_puc_count": counter_data.get("invalid_puc_count", 0)
        }
