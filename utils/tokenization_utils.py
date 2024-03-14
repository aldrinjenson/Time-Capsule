# utils/tokenization_utils.py
"""
Tokenization utilities for the Time Capsule application.

This module provides the TokenizationUtils class, which handles text tokenization,
preprocessing, and storage of tokenized entries. It integrates with the NLTK library
for tokenization and supports processing text from various sources such as text capture,
OCR, and Whisper transcripts.
"""

import os
import json
import uuid
import nltk
import logging

class TokenizationUtils:
    """Class for text tokenization and storage."""

    def __init__(self, output_dir):
        """
        Initialize the TokenizationUtils.

        Args:
            output_dir (str): Output directory for storing tokenized entries.
        """
        self.output_dir = output_dir
        self.current_entry = None
        self.token_limit = 2000  # Adjust the token limit based on your model's context window
        nltk.download('punkt')  # Download the required NLTK data
        self.logger = logging.getLogger(__name__)

    def is_token_limit_reached(self, text):
        """Check if the token limit is reached for the given text."""
        tokens = nltk.word_tokenize(text)
        return len(tokens) >= self.token_limit

    def preprocess_text(self, text):
        """Preprocess the text by removing unnecessary whitespace and non-text characters."""
        clean_text = " ".join(text.split())
        return clean_text

    def tokenize_and_store_text(self, text, timestamp, source, metadata=None, context_switch=False):
        """Tokenize and store the text entry."""
        clean_text = self.preprocess_text(text)

        if self.current_entry is None or context_switch:
            if self.current_entry is not None:
                self.store_entry(self.current_entry)
            self.current_entry = {
                "id": str(uuid.uuid4()),
                "timestamp": timestamp,
                "source": source,
                "text": clean_text,
                "metadata": metadata
            }
        else:
            self.current_entry["text"] += " " + clean_text

        # Print the current entry to the console
        print(json.dumps(self.current_entry, indent=2))

        # Check if the current entry reaches the token limit
        if self.is_token_limit_reached(self.current_entry["text"]):
            self.store_entry(self.current_entry)
            self.current_entry = None

    def store_entry(self, entry):
        """Store the tokenized entry as a JSON file."""
        try:
            filename = f"entry_{entry['timestamp']}.json"
            filepath = os.path.join(self.output_dir, filename)
            entry["tokens"] = nltk.word_tokenize(entry["text"])
            with open(filepath, 'w') as file:
                json.dump(entry, file, indent=2)
        except Exception as e:
            self.logger.error(f"Error storing entry: {str(e)}")

    def process_text_capture(self, text, timestamp, metadata=None, context_switch=False):
        """Process text captured from the text capture module."""
        self.tokenize_and_store_text(text, timestamp, "Text Capture", metadata, context_switch)

    def process_ocr_text(self, text, timestamp, metadata=None):
        """Process text extracted from OCR."""
        self.tokenize_and_store_text(text, timestamp, "OCR", metadata)

    def process_whisper_transcript(self, text, timestamp, metadata=None):
        """Process text from Whisper transcripts."""
        self.tokenize_and_store_text(text, timestamp, "Whisper Transcript", metadata)