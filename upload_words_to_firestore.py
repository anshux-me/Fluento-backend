"""
Upload Words to Firestore

This script uploads all words from wordnet_full.json to Firestore,
organized by difficulty level for efficient querying.

Run: python upload_words_to_firestore.py
"""

import json
import time
import firebase_admin
from firebase_admin import credentials, firestore
from pathlib import Path

# Initialize Firebase Admin SDK
cred_path = Path(__file__).parent / "firebase-credentials.json"
if not firebase_admin._apps:
    cred = credentials.Certificate(str(cred_path))
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Smaller batch size to avoid timeouts
BATCH_SIZE = 200


def upload_words():
    """Upload all words to Firestore organized by difficulty."""
    
    # Load words from JSON
    words_file = Path(__file__).parent.parent / "wordnet_full.json"
    if not words_file.exists():
        words_file = Path(__file__).parent / "data" / "words.json"
    
    print(f"Loading words from {words_file}...")
    with open(words_file, "r", encoding="utf-8") as f:
        words = json.load(f)
    
    print(f"Loaded {len(words)} words")
    
    # Count words by difficulty
    counts = {"easy": 0, "medium": 0, "hard": 0}
    
    # Organize words by difficulty
    words_by_difficulty = {"easy": [], "medium": [], "hard": []}
    
    for word in words:
        difficulty = word.get("difficulty", "Medium").lower()
        if difficulty in words_by_difficulty:
            words_by_difficulty[difficulty].append(word)
            counts[difficulty] += 1
    
    print(f"\nWord counts by difficulty:")
    for diff, count in counts.items():
        print(f"  {diff}: {count}")
    
    # Upload each difficulty collection (skip easy - already uploaded)
    for difficulty, word_list in words_by_difficulty.items():
        collection_name = f"words_{difficulty}"
        
        # Skip easy words - already uploaded
        if difficulty == "easy":
            print(f"\nSkipping '{collection_name}' - already uploaded")
            continue
        
        print(f"\nUploading {len(word_list)} words to '{collection_name}'...")
        
        batch = db.batch()
        batch_count = 0
        total_uploaded = 0
        max_retries = 3
        
        for i, word_data in enumerate(word_list):
            # Create document with word as ID (sanitized)
            doc_id = f"{word_data['word']}_{i}"  # Add index to handle duplicates
            doc_ref = db.collection(collection_name).document(doc_id)
            
            # Prepare document data
            doc_data = {
                "word": word_data.get("word", ""),
                "pos": word_data.get("pos", ""),
                "difficulty": word_data.get("difficulty", "Medium"),
                "definitions": word_data.get("definitions", []),
                "examples": word_data.get("examples", []),
                "synonyms": word_data.get("synonyms", []),
                "antonyms": word_data.get("antonyms", []),
                "index": i  # For random selection
            }
            
            batch.set(doc_ref, doc_data)
            batch_count += 1
            
            # Commit batch when full
            if batch_count >= BATCH_SIZE:
                for attempt in range(max_retries):
                    try:
                        batch.commit()
                        break
                    except Exception as e:
                        if attempt < max_retries - 1:
                            print(f"  Retry {attempt + 1}/{max_retries}...")
                            time.sleep(2 ** attempt)  # Exponential backoff
                        else:
                            print(f"  Error after {max_retries} retries: {e}")
                            raise
                
                total_uploaded += batch_count
                print(f"  Uploaded {total_uploaded}/{len(word_list)} words...")
                batch = db.batch()
                batch_count = 0
                time.sleep(0.5)  # Small delay to avoid rate limits
        
        # Commit remaining documents
        if batch_count > 0:
            for attempt in range(max_retries):
                try:
                    batch.commit()
                    break
                except Exception as e:
                    if attempt < max_retries - 1:
                        print(f"  Retry {attempt + 1}/{max_retries}...")
                        time.sleep(2 ** attempt)
                    else:
                        raise
            total_uploaded += batch_count
        
        print(f"  ✓ Completed uploading to '{collection_name}'")
    
    # Store metadata with counts
    print("\nStoring word count metadata...")
    metadata_ref = db.collection("metadata").document("word_counts")
    metadata_ref.set({
        "easy": counts["easy"],
        "medium": counts["medium"],
        "hard": counts["hard"],
        "total": sum(counts.values()),
        "updated_at": firestore.SERVER_TIMESTAMP
    })
    
    print("\n✓ Upload complete!")
    print(f"Total words uploaded: {sum(counts.values())}")


if __name__ == "__main__":
    upload_words()
