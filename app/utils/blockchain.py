from app import db
from app.models.blockchain import BlockchainRecord
from datetime import datetime
import json
import hashlib

class BlockchainManager:
    
    @staticmethod
    def initialize_blockchain():
        """Initialize blockchain with genesis block if not exists"""
        genesis = BlockchainRecord.query.filter_by(block_index=0).first()
        if not genesis:
            genesis = BlockchainRecord.create_genesis_block()
            db.session.add(genesis)
            db.session.commit()
            return genesis
        return genesis
    
    @staticmethod
    def get_latest_block():
        """Get the latest block in the chain"""
        return BlockchainRecord.query.order_by(BlockchainRecord.block_index.desc()).first()
    
    @staticmethod
    def add_block(data_dict, record_type='registration'):
        """Add a new block to the blockchain"""
        latest_block = BlockchainManager.get_latest_block()
        
        if not latest_block:
            latest_block = BlockchainManager.initialize_blockchain()
        
        new_index = latest_block.block_index + 1
        timestamp = datetime.utcnow().isoformat()
        data = json.dumps(data_dict, default=str)
        previous_hash = latest_block.current_hash
        
        nonce = 0
        current_hash = BlockchainRecord.calculate_hash(new_index, timestamp, data, previous_hash, nonce)
        
        new_block = BlockchainRecord(
            block_index=new_index,
            timestamp=datetime.utcnow(),
            data=data,
            previous_hash=previous_hash,
            current_hash=current_hash,
            nonce=nonce,
            record_type=record_type
        )
        
        db.session.add(new_block)
        db.session.commit()
        
        return new_block
    
    @staticmethod
    def verify_chain():
        """Verify the integrity of the blockchain"""
        blocks = BlockchainRecord.query.order_by(BlockchainRecord.block_index).all()
        
        for i in range(1, len(blocks)):
            current_block = blocks[i]
            previous_block = blocks[i - 1]
            
            if current_block.previous_hash != previous_block.current_hash:
                return False, f"Block {current_block.block_index} has invalid previous hash"
            
            calculated_hash = BlockchainRecord.calculate_hash(
                current_block.block_index,
                current_block.timestamp.isoformat(),
                current_block.data,
                current_block.previous_hash,
                current_block.nonce
            )
            
            if current_block.current_hash != calculated_hash:
                return False, f"Block {current_block.block_index} has invalid hash"
        
        return True, "Blockchain is valid"
    
    @staticmethod
    def get_block_by_hash(block_hash):
        """Retrieve a block by its hash"""
        return BlockchainRecord.query.filter_by(current_hash=block_hash).first()
    
    @staticmethod
    def get_all_blocks():
        """Get all blocks ordered by index"""
        return BlockchainRecord.query.order_by(BlockchainRecord.block_index).all()
