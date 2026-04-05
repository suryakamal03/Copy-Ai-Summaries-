import os
import hashlib
import re
from dotenv import load_dotenv
from google import genai
from chromadb import CloudClient

load_dotenv()

class RAGChat:
    def __init__(self):
        """Initialize ChromaDB Cloud client and Gemini"""
        # Load environment variables
        chroma_api_key = os.getenv("CHROMA_API_KEY")
        chroma_tenant = os.getenv("CHROMA_TENANT")
        chroma_database = os.getenv("CHROMA_DATABASE")
        gemini_api_key = os.getenv("GOOGLE_GEMINI_API_KEY")
        
        if not all([chroma_api_key, chroma_tenant, chroma_database]):
            raise ValueError("ChromaDB credentials not found in .env file")
        
        if not gemini_api_key:
            raise ValueError("Gemini API key not found in .env file")
        
        # Initialize ChromaDB Cloud Client
        self.client = CloudClient(
            api_key=chroma_api_key,
            tenant=chroma_tenant,
            database=chroma_database
        )
        
        # Initialize Gemini client
        self.gemini_client = genai.Client(api_key=gemini_api_key)
    
    @staticmethod
    def generate_video_id(video_url):
        """Generate a unique collection ID from video URL"""
        return hashlib.md5(video_url.encode()).hexdigest()[:16]
    
    def correct_transcript(self, transcript):
        """
        Use Gemini to correct transcription errors in the transcript
        Focuses on technical terms, tool names, and common YouTube transcript errors
        """
        try:
            print("Running Gemini spell-check on transcript...")
            
            # Don't correct if transcript is too short
            if len(transcript) < 100:
                return transcript
            
            correction_prompt = f"""You are a transcript correction assistant. Your job is to identify and correct transcription errors in YouTube video transcripts.

Common issues to fix:
- Misheard technical terms (e.g., "end mapap" → "nmap", "cubeectl" → "kubectl")
- Tool and software names (e.g., "docker" not "darker", "Python" not "pie thon")
- Programming languages and frameworks
- Acronyms and abbreviations
- Technical jargon that was phonetically transcribed wrong

IMPORTANT RULES:
1. ONLY fix clear transcription errors
2. DO NOT change the meaning or add information
3. DO NOT rephrase sentences
4. Preserve the original structure and timing context
5. Keep ALL words - only fix spelling/accuracy
6. If unsure, leave it unchanged

Original Transcript:
{transcript[:3000]}{"..." if len(transcript) > 3000 else ""}

Corrected Transcript (output ONLY the corrected text, no explanations):"""

            response = self.gemini_client.models.generate_content(
                model="gemini-flash-latest",
                contents=correction_prompt
            )
            
            corrected_transcript = response.text.strip()
            
            # If correction seems to have drastically changed length, use original
            length_ratio = len(corrected_transcript) / len(transcript)
            if length_ratio < 0.8 or length_ratio > 1.2:
                print("Warning: Correction changed transcript length significantly, using original")
                return transcript
            
            print("Transcript corrected successfully")
            return corrected_transcript
            
        except Exception as e:
            print(f"Error correcting transcript: {e}")
            print("Using original transcript")
            return transcript
    
    @staticmethod
    def chunk_text(text, chunk_size=500, overlap=50):
        """
        Split text into chunks with overlap
        chunk_size: number of words per chunk
        overlap: number of words to overlap between chunks
        """
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            if chunk:
                chunks.append(chunk)
        
        return chunks

    @staticmethod
    def _safe_preview(text, max_len=260):
        value = (text or "").strip().replace("\n", " ")
        if len(value) <= max_len:
            return value
        return value[:max_len].rstrip() + "..."

    @staticmethod
    def _greeting_response(relevant_chunks):
        snippet = RAGChat._safe_preview(relevant_chunks[0] if relevant_chunks else "")
        return (
            "Hi! I analyzed this video for you. "
            "It discusses a software/security topic and explains key events and practical checks to perform. "
            "\n\nTry asking:\n"
            "1. What is the main issue explained in this video?\n"
            "2. What steps should I take to stay safe?\n"
            "3. Give me the key points in bullet form."
            + (f"\n\nQuick excerpt: \"{snippet}\"" if snippet else "")
        )

    @staticmethod
    def _fallback_answer_from_context(question, relevant_chunks):
        snippet = RAGChat._safe_preview(relevant_chunks[0] if relevant_chunks else "")
        if not snippet:
            return "I couldn't find that clearly in this video."
        return (
            "I couldn't use the AI model right now, so here is the best answer from the transcript context:\n\n"
            f"{snippet}"
        )
    
    def ingest_transcript(self, video_url, transcript, video_title="", enable_correction=False):
        """
        Chunk transcript and store in ChromaDB
        Returns: collection_id
        """
        try:
            # Generate collection ID
            collection_id = self.generate_video_id(video_url)
            
            # Correct transcript using Gemini before chunking
            if enable_correction:
                transcript = self.correct_transcript(transcript)
            
            # Chunk the transcript
            chunks = self.chunk_text(transcript, chunk_size=500, overlap=50)
            
            if not chunks:
                raise ValueError("No chunks generated from transcript")
            
            print(f"Generated {len(chunks)} chunks from transcript")
            
            # Delete existing collection if it exists to ensure fresh data
            try:
                self.client.delete_collection(name=collection_id)
                print(f"Deleted existing collection: {collection_id}")
            except:
                pass
            
            # Create new collection
            collection = self.client.create_collection(
                name=collection_id,
                metadata={"video_url": video_url, "title": video_title}
            )
            print(f"Created collection: {collection_id}")
            
            # Prepare documents and IDs
            ids = [f"chunk_{i}" for i in range(len(chunks))]
            metadatas = [{"chunk_index": i, "video_url": video_url} for i in range(len(chunks))]
            
            # Add chunks to collection (ChromaDB auto-generates embeddings)
            collection.add(
                documents=chunks,
                ids=ids,
                metadatas=metadatas
            )
            
            print(f"Added {len(chunks)} chunks to collection {collection_id}")
            return collection_id
        
        except Exception as e:
            raise Exception(f"Failed to ingest transcript: {str(e)}")
    
    def query_chat(self, video_url, question, n_results=5):
        """
        Query ChromaDB and generate answer using RAG
        """
        try:
            # Get collection ID
            collection_id = self.generate_video_id(video_url)
            print(f"Querying collection: {collection_id} with question: {question}")
            
            # Get collection
            try:
                collection = self.client.get_collection(name=collection_id)
                count = collection.count()
                print(f"Collection has {count} documents")
                
                # Check if collection is empty
                if count == 0:
                    print("Collection is empty - transcript not ingested yet")
                    return {
                        "answer": "The video transcript is still being processed. Please wait a moment and try again.",
                        "sources": []
                    }
            except Exception as e:
                print(f"Collection not found: {e}")
                return {
                    "answer": "Please generate a summary first to initialize the chat system.",
                    "sources": []
                }
            
            q = (question or "").strip()
            is_greeting = bool(re.fullmatch(r"(?i)\s*(hi|hello|hey|yo|sup|hola|vanakkam)\s*[!.?]*\s*", q))

            # Query ChromaDB for relevant chunks
            results = collection.query(
                query_texts=[question],
                n_results=n_results
            )
            
            print(f"Query results: {results}")
            
            # Extract relevant chunks
            if not results or not results.get('documents') or not results['documents'][0]:
                print("No results found")
                return {
                    "answer": "This information is not mentioned in the video.",
                    "sources": []
                }
            
            relevant_chunks = results['documents'][0]
            print(f"Found {len(relevant_chunks)} relevant chunks")
            context = "\n\n".join(relevant_chunks)
            
            if is_greeting:
                return {
                    "answer": self._greeting_response(relevant_chunks),
                    "sources": relevant_chunks[:2]
                }
            else:
                prompt = f"""You are a helpful assistant that answers questions based ONLY on the provided video transcript context.

RULES:
1. Answer ONLY using the context below.
2. If context is insufficient, say: "I couldn't find that clearly in this video."
3. Do NOT use external knowledge.
4. Be concise and direct.
5. When possible, include a short quote-like phrase from context.

CONTEXT FROM VIDEO TRANSCRIPT:
{context}

USER QUESTION:
{question}

ANSWER:"""

            try:
                response = self.gemini_client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )
                answer = (response.text or "").strip()
                if not answer:
                    answer = self._fallback_answer_from_context(question, relevant_chunks)
            except Exception as model_error:
                print(f"Gemini query failed, using context fallback: {model_error}")
                answer = self._fallback_answer_from_context(question, relevant_chunks)
            
            return {
                "answer": answer,
                "sources": relevant_chunks[:2]  # Return top 2 source chunks
            }
        
        except Exception as e:
            raise Exception(f"Failed to query chat: {str(e)}")
    
    def check_collection_exists(self, video_url):
        """Check if transcript is already ingested"""
        try:
            collection_id = self.generate_video_id(video_url)
            self.client.get_collection(name=collection_id)
            return True
        except:
            return False
