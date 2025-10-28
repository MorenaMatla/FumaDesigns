from app import db
from datetime import datetime
import hashlib
import json

class BlockchainRecord(db.Model):
    __tablename__ = 'blockchain_records'
    
    id = db.Column(db.Integer, primary_key=True)
    block_index = db.Column(db.Integer, unique=True, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    data = db.Column(db.Text, nullable=False)
    previous_hash = db.Column(db.String(64), nullable=False)
    current_hash = db.Column(db.String(64), unique=True, nullable=False)
    nonce = db.Column(db.Integer, default=0)
    record_type = db.Column(db.String(50), nullable=False)
    
    def __repr__(self):
        return f'<BlockchainRecord {self.block_index} - {self.record_type}>'
    
    @staticmethod
    def calculate_hash(index, timestamp, data, previous_hash, nonce):
        block_string = f"{index}{timestamp}{data}{previous_hash}{nonce}"
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    @staticmethod
    def create_genesis_block():
        genesis_data = json.dumps({
            'type': 'genesis',
            'message': 'Genesis Block - Exam Registration System',
            'created_at': datetime.utcnow().isoformat()
        })
        genesis_hash = BlockchainRecord.calculate_hash(0, datetime.utcnow().isoformat(), genesis_data, "0", 0)
        
        genesis_block = BlockchainRecord(
            block_index=0,
            data=genesis_data,
            previous_hash="0",
            current_hash=genesis_hash,
            record_type='genesis'
        )
        return genesis_block
