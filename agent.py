import re
import PyPDF2
import io
import sys
import os
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
import tempfile
import json
import warnings
import httpx

# Suppress warnings
warnings.filterwarnings('ignore')

# Ensure UTF-8 encoding for all output
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass
if sys.stderr.encoding != 'utf-8':
    try:
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass

# Set UTF-8 environment variables
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['PYTHONLEGACYWINDOWSSTDIO'] = '0'
os.environ['LC_ALL'] = 'en_US.UTF-8'
os.environ['LANG'] = 'en_US.UTF-8'

# Configure httpx to use UTF-8
httpx.Client.encoding = 'utf-8'

class ResumeAnalysisAgent:
    def __init__(self,api_key,cutoff_score=75):
        self.api_key = api_key
        # Keep API key as-is (don't sanitize it as it needs to be exact)
        self.cutoff_score = cutoff_score
        self.resume_text=None
        self.rag_vectorstore=None
        self.analysis_results=None
        self.jd_text=None
        self.extracted_skills=None
        self.resume_weaknesses=[]
        self.resume_strengths=[]
        self.improvement_suggestions=[]
        # Initialize embeddings with UTF-8 HTTP client
        try:
            http_client = httpx.Client(encoding='utf-8')
            self.embeddings = OpenAIEmbeddings(openai_api_key=self.api_key, http_client=http_client)
        except:
            # Fallback to default initialization
            self.embeddings = OpenAIEmbeddings(openai_api_key=self.api_key)
        # Set up FAISS index directory
        self.faiss_index_dir = 'faiss_indexes'
        if not os.path.exists(self.faiss_index_dir):
            os.makedirs(self.faiss_index_dir)
    
    def _ensure_utf8(self, text):
        """Ensure text is properly encoded as UTF-8 string"""
        if isinstance(text, bytes):
            return text.decode('utf-8', errors='replace')
        elif isinstance(text, str):
            return text
        else:
            return str(text)
    
    def _sanitize_text(self, text):
        """Remove problematic characters that might cause encoding issues"""
        if not text:
            return ""
        # Ensure it's a string
        text = self._ensure_utf8(text)
        # Keep only ASCII characters and common UTF-8 that won't cause issues
        # Remove control characters and problematic unicode
        safe_text = ""
        for char in text:
            # Keep only ASCII printable characters and common whitespace
            if ord(char) < 128 and (char.isprintable() or char.isspace()):
                safe_text += char
            elif ord(char) >= 128:
                # For non-ASCII, try to keep if it's a letter/digit
                try:
                    if char.isalnum() or char in ['-', '_', '.', ',', ':', ';', '!', '?', "'", '"']:
                        safe_text += char
                    else:
                        # Replace with space to preserve word boundaries
                        safe_text += " "
                except:
                    safe_text += " "
        return safe_text

    def extract_text_from_pdf(self, pdf_bytes):
        '''Extract text from PDF File.'''
        try:
            if hasattr(pdf_bytes, 'getvalue'):
                pdf_data = pdf_bytes.getvalue()
                pdf_file_like = io.BytesIO(pdf_data)
                reader = PyPDF2.PdfReader(pdf_file_like)
            else:
                reader = PyPDF2.PdfReader(pdf_bytes)

            text = ""
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    # Ensure proper encoding handling
                    if isinstance(page_text, bytes):
                        page_text = page_text.decode('utf-8', errors='replace')
                    text += page_text + "\n"
            return text
        except Exception as e:
            print(f"Error extracting text from PDF: {str(e)}")
            return ""
        
    def extract_text_from_txt(self, txt_file):
        '''Extract text from TXT File.'''
        try:        
            if hasattr(txt_file, 'getvalue'):
                txt_data = txt_file.getvalue()
                if isinstance(txt_data, bytes):
                    return txt_data.decode('utf-8', errors='replace')
                return txt_data
            else:
                with open(txt_file, 'r', encoding='utf-8') as f:
                    return f.read()             
        except Exception as e:
            print(f"Error extracting text from TXT: {str(e)}")
            return ""  

    def extract_text_from_file(self, file):
        '''Extract text from file (PDF or text).'''
        if file.name.lower().endswith('.pdf'):
            return self.extract_text_from_pdf(file)
        elif file.name.lower().endswith('.txt'):
            return self.extract_text_from_txt(file)
        else:
            print("Unsupported file format. Please upload a PDF or TXT file.")
            return ""
            
    def create_rag_vector_store(self, text):
        '''Create RAG Vector Store from text.'''
        try:
            # Ensure text is properly encoded as UTF-8
            if isinstance(text, bytes):
                text = text.decode('utf-8', errors='replace')
            
            # Sanitize text to remove problematic characters
            text = self._sanitize_text(text)
            
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len,  
            )
            chunks = text_splitter.split_text(text)
            
            # Sanitize each chunk as well and remove empty chunks
            chunks = [self._sanitize_text(chunk).strip() for chunk in chunks if chunk.strip()]
            
            if not chunks:
                print("No chunks to process after sanitization")
                return None
            
            # Remove any chunks that are too short or contain only whitespace
            chunks = [chunk for chunk in chunks if len(chunk.strip()) > 10]
            
            if not chunks:
                # If no valid chunks, create a dummy chunk from sanitized text
                chunks = [text[:1000] if text else "Resume content"]
            
            embeddings = OpenAIEmbeddings(openai_api_key=self.api_key)
            vectorstore = FAISS.from_texts(chunks, embeddings)
            return vectorstore
        except Exception as e:
            print(f"Error creating RAG vector store: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def create_vector_store(self, text):
        '''Create a simpler vector store for skill analysis.'''
        try:
            # Ensure text is properly encoded as UTF-8
            if isinstance(text, bytes):
                text = text.decode('utf-8', errors='replace')
            
            # Sanitize text
            text = self._sanitize_text(text)
            
            # Make sure text is not empty
            if not text or len(text.strip()) == 0:
                text = "Resume content"
            
            embeddings = OpenAIEmbeddings(openai_api_key=self.api_key)
            vectorstore = FAISS.from_texts([text[:2000]], embeddings)
            return vectorstore
        except Exception as e:
            print(f"Error creating vector store: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def analyze_resume_weaknesses(self):
        '''Analyze resume weaknesses based on extracted skills.'''
        if not self.resume_text or not self.extracted_skills or not self.analysis_results:
            return []
        weaknesses = []

        for skill in self.analysis_results.get("missing_skills", []):
            weakness_detail = {
                "skill": skill,
                "score": self.analysis_results.get("skill_scores", {}).get(skill, 0),
                "detail": "Skill needs improvement - consider adding relevant projects or certifications",
                "suggestions": [
                    "Add a project showcasing this skill to your experience section",
                    "Include relevant certifications or training courses",
                    "Highlight specific accomplishments using this skill"
                ],
                "example": f"Led implementation of {skill} solution resulting in 30% efficiency improvement"
            }
            
            try:
                # Create custom HTTP client with UTF-8 encoding
                try:
                    http_client = httpx.Client(encoding='utf-8')
                    llm = ChatOpenAI(
                        model="gpt-4o", 
                        openai_api_key=self.api_key, 
                        temperature=0.5,
                        http_client=http_client
                    )
                except:
                    # Fallback without custom HTTP client
                    llm = ChatOpenAI(model="gpt-4o", openai_api_key=self.api_key, temperature=0.5)
                
                # Sanitize all inputs
                sanitized_skill = self._sanitize_text(skill)
                sanitized_resume = self._sanitize_text(self.resume_text[:3000])
                
                prompt = (f"The resume lacks the skill: {sanitized_skill}. Suggest ways to improve the resume to better demonstrate this skill. "
                          "For your analysis, consider: "
                          "1. Whats missing in the resume regarding this skill? "
                          "2. How it can be improved with specific examples? "
                          "3. Provide actionable suggestions. "
                          f"Resume Content: {sanitized_resume} "
                          "Provide your response in JSON format with keys: "
                          '{"weakness":"A concise description of what\'s missing or problematic (1-2 sentences)",'
                          '"improvement_suggestions":["Specific suggestion 1","Specific suggestion 2","Specific suggestion 3"],'
                          '"example_addition":"A specific bullet point that could be added to showcase this skill"} '
                          "Return only the JSON object without any additional text.")

                response = llm.invoke(prompt)
                weakness_content = response.content.strip()
                
                try:
                    weakness_data = json.loads(weakness_content)
                    weakness_detail = {
                        "skill": skill,
                        "score": self.analysis_results.get("skill_scores", {}).get(skill, 0),
                        "detail": weakness_data.get("weakness", "No Specific details provided."),
                        "suggestions": weakness_data.get("improvement_suggestions", []),
                        "example": weakness_data.get("example_addition", "")
                    }

                    self.improvement_suggestions[skill] = {
                        "suggestions": weakness_data.get("improvement_suggestions", []),
                        "example": weakness_data.get("example_addition", "")
                    }           
                except json.JSONDecodeError:
                    pass
                    
            except UnicodeEncodeError as ue:
                print(f"Encoding error analyzing weakness for skill {skill}: {str(ue)}")
                weakness_detail["detail"] = "Skill needs improvement - consider adding relevant experience"
            except Exception as e:
                print(f"Error analyzing weakness for skill {skill}: {str(e)}")
                weakness_detail["detail"] = "Skill needs improvement - add more relevant experience"
            
            weaknesses.append(weakness_detail)

        self.resume_weaknesses = weaknesses
        return weaknesses
    
    def extract_skills_from_jd(self, jd_text):
        '''Extract skills from Job Description text.'''
        try:
            llm = ChatOpenAI(model="gpt-4o", api_key=self.api_key, temperature=0.5)
            prompt = (f"Extract and list the key skills required for the job from the following job description:\n\n{jd_text}\n\n"
                      "Format the output as a Python list of strings. Only provide the list without any additional text.")
            response = llm.invoke(prompt)
            skills_text = response.content.strip()

            match = re.search(r'\[.*\]', skills_text, re.DOTALL)
            if match:
                skills_text = match.group(0)

            try:
                skills_list = eval(skills_text)
                if isinstance(skills_list, list):
                    return skills_list
            except:
                pass

            skills = []
            for line in skills_text.split('\n'):
                line = line.strip()
                if line.startswith('- ') or line.startswith('* '):
                    skill = line[2:].strip()
                    if skill:
                        skills.append(skill)

                elif line.startswith('"') and line.endswith('"'):
                    skill = line.strip('"').strip()
                    if skill:
                        skills.append(skill)

            return skills
        except Exception as e:
            print(f"Error extracting skills from JD: {e}")
            return []
        
    def semantic_skill_analysis(self, resume_text, skills):
        '''Perform semantic skill analysis of resume against extracted skills.'''
        try:
            # Try to use vector store first, fall back to direct analysis if it fails
            return self._vector_store_analysis(resume_text, skills)
        except Exception as e:
            print(f"Error in vector store analysis: {str(e)}, falling back to direct analysis")
            try:
                return self._direct_skill_analysis(resume_text, skills)
            except Exception as e2:
                print(f"Error in fallback direct analysis: {str(e2)}")
                import traceback
                traceback.print_exc()
                return None
    
    def _vector_store_analysis(self, resume_text, skills):
        """Vector store based semantic skill analysis using FAISS"""
        try:
            # Create or load FAISS vectorstore from resume
            vectorstore = self._get_or_create_vectorstore(resume_text)
            
            skill_scores = {}
            skill_reasonings = {}
            missing_skills = []
            total_score = 0
            
            # Create custom HTTP client with UTF-8 encoding for LLM
            try:
                http_client = httpx.Client(encoding='utf-8')
                llm = ChatOpenAI(
                    model="gpt-4o", 
                    openai_api_key=self.api_key, 
                    temperature=0,
                    http_client=http_client
                )
            except:
                llm = ChatOpenAI(model="gpt-4o", openai_api_key=self.api_key, temperature=0)
            
            for skill in skills:
                try:
                    sanitized_skill = self._sanitize_text(skill)
                    
                    # Query vectorstore for skill relevance
                    results = vectorstore.similarity_search(sanitized_skill, k=3)
                    context = "\n".join([doc.page_content for doc in results]) if results else ""
                    
                    prompt = f"On a scale of 0 to 10, how well does this resume demonstrate proficiency in {sanitized_skill}?\n\nRelevant resume content:\n{context}"
                    response = llm.invoke(prompt)
                    response_text = response.content.strip()
                    
                    match = re.search(r'(\d{1,2})', response_text)
                    score = int(match.group(1)) if match else 5
                    score = min(score, 10)
                    reasoning = response_text
                    
                except UnicodeEncodeError as ue:
                    print(f"Encoding error in vector store analysis for {skill}: {str(ue)}")
                    score = 5
                    reasoning = "Analysis skipped due to encoding issues"
                except Exception as e:
                    print(f"Error analyzing {skill} with vector store: {str(e)}")
                    score = 5
                    reasoning = f"Error: {str(e)[:50]}"
                
                skill_scores[skill] = score
                skill_reasonings[skill] = reasoning
                total_score += score
                
                if score <= 5:
                    missing_skills.append(skill)
            
            overall_score = int((total_score / (len(skills) * 10)) * 100) if skills else 0
            selected = overall_score >= self.cutoff_score
            self.resume_strengths = [skill for skill, score in skill_scores.items() if score >= 7]
            
            return {
                "overall_score": overall_score,
                "skill_scores": skill_scores,
                "skill_reasonings": skill_reasonings,
                "selected": selected,
                "reasoning": "Vector store based semantic analysis",
                "missing_skills": missing_skills,
                "strengths": self.resume_strengths,
                "improvement_areas": missing_skills if not selected else []
            }
        except Exception as e:
            print(f"Error in vector store analysis: {str(e)}")
            raise
    
    def _get_or_create_vectorstore(self, text):
        """Get or create FAISS vectorstore from text - creates fresh index each time"""
        import uuid
        import shutil
        
        # Use a unique index name for each analysis to avoid stale data
        unique_id = str(uuid.uuid4())[:8]
        index_name = f'resume_index_{unique_id}'
        index_path = os.path.join(self.faiss_index_dir, index_name)
        
        # Create new vectorstore for each analysis (fresh start)
        print("Creating new FAISS vectorstore for fresh analysis...")
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = text_splitter.split_text(text[:5000])  # Limit text for embedding
        
        try:
            http_client = httpx.Client(encoding='utf-8')
            embeddings = OpenAIEmbeddings(openai_api_key=self.api_key, http_client=http_client)
        except:
            embeddings = OpenAIEmbeddings(openai_api_key=self.api_key)
        
        vectorstore = FAISS.from_texts(chunks, embeddings)
        
        # Save to disk with unique name
        try:
            vectorstore.save_local(index_path)
            print(f"Saved FAISS index to {index_path}")
        except Exception as e:
            print(f"Could not save FAISS index: {e}")
        
        # Clean up old indexes (keep only last 3)
        try:
            import glob
            all_indexes = glob.glob(os.path.join(self.faiss_index_dir, 'resume_index_*'))
            if len(all_indexes) > 3:
                all_indexes.sort(key=os.path.getctime)
                for old_index in all_indexes[:-3]:
                    try:
                        shutil.rmtree(old_index)
                        print(f"Cleaned up old index: {old_index}")
                    except:
                        pass
        except Exception as e:
            print(f"Could not clean up old indexes: {e}")
        
        return vectorstore
    
    def _direct_skill_analysis(self, resume_text, skills):
        """Fallback method for direct skill analysis without vector store"""
        try:
            skill_scores = {}
            skill_reasonings = {}
            missing_skills = []
            total_score = 0

            for skill in skills:
                score = 0
                reasoning = ""
                try:
                    # Create custom HTTP client with UTF-8 encoding
                    try:
                        http_client = httpx.Client(encoding='utf-8')
                        llm = ChatOpenAI(
                            model="gpt-4o", 
                            openai_api_key=self.api_key, 
                            temperature=0,
                            http_client=http_client
                        )
                    except:
                        # Fallback without custom HTTP client
                        llm = ChatOpenAI(model="gpt-4o", openai_api_key=self.api_key, temperature=0)
                    
                    # Sanitize skill name
                    skill = self._sanitize_text(skill)
                    # Sanitize resume text for this analysis
                    sanitized_resume = self._sanitize_text(resume_text[:2000])
                    
                    question = f"On a scale of 0 to 10, how well does this resume demonstrate proficiency in {skill}?\n\nResume:\n{sanitized_resume}"
                    response = llm.invoke(question)
                    response_text = response.content.strip()
                    
                    match = re.search(r'(\d{1,2})', response_text)
                    score = int(match.group(1)) if match else 5
                    score = min(score, 10)
                    reasoning = response_text
                    
                except UnicodeEncodeError as ue:
                    print(f"Encoding error in direct analysis for {skill}: {str(ue)}")
                    # Use default score of 5 for encoding errors
                    score = 5
                    reasoning = "Analysis skipped due to encoding issues - assuming neutral skill level"
                except Exception as e:
                    print(f"Error in direct analysis for {skill}: {str(e)}")
                    # Use default score of 5 for other errors
                    score = 5
                    reasoning = f"Analysis skipped: {str(e)[:50]}"
                
                skill_scores[skill] = score
                skill_reasonings[skill] = reasoning
                total_score += score
                
                if score <= 5:
                    missing_skills.append(skill)

            overall_score = int((total_score / (len(skills) * 10)) * 100) if skills else 0
            selected = overall_score >= self.cutoff_score

            self.resume_strengths = [skill for skill, score in skill_scores.items() if score >= 7]

            return {
                "overall_score": overall_score,
                "skill_scores": skill_scores,
                "skill_reasonings": skill_reasonings,
                "selected": selected,
                "reasoning": "Direct analysis without vector store",
                "missing_skills": missing_skills,
                "strengths": self.resume_strengths,
                "improvement_areas": missing_skills if not selected else []
            }
        except Exception as e:
            print(f"Error in direct skill analysis: {str(e)}")
            import traceback
            traceback.print_exc()
            return None


    def analyze_resume(self, resume_file, role_requirements=None, custom_jd=None):
        '''Main method to analyze resume against job description or role requirements.'''
        try:
            self.resume_text = self.extract_text_from_file(resume_file)
            self.resume_text = self._ensure_utf8(self.resume_text)
            
            if not self.resume_text:
                print("Failed to extract text from resume.")
                return None
            
            # Write to temp file with proper encoding
            with tempfile.NamedTemporaryFile(delete=False, suffix='.txt', mode='w', encoding='utf-8', errors='replace') as tmp:
                tmp.write(self.resume_text)
                self.resume_file_path = tmp.name

            if custom_jd:
                self.jd_text = self.extract_text_from_file(custom_jd)
                self.jd_text = self._ensure_utf8(self.jd_text)
                self.extracted_skills = self.extract_skills_from_jd(self.jd_text)
                self.analysis_results = self.semantic_skill_analysis(self.resume_text, self.extracted_skills)
            elif role_requirements:
                self.extracted_skills = role_requirements
                self.analysis_results = self.semantic_skill_analysis(self.resume_text, role_requirements)

            if self.analysis_results and "missing_skills" in self.analysis_results and self.analysis_results["missing_skills"]:
                self.analyze_resume_weaknesses()
                self.analysis_results["resume_weaknesses"] = self.resume_weaknesses

            return self.analysis_results
        except Exception as e:
            error_msg = f"Error in analyze_resume: {str(e)}"
            print(error_msg)
            raise Exception(error_msg) from e
            
        
                    



                    

                
                  



                