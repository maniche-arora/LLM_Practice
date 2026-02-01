import streamlit as st
from agent import ResumeAnalysisAgent
from ui import ResumeAnalysisUI
import os
import sys
import config  # Import configuration

# Ensure UTF-8 encoding for Streamlit
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


class ResumeAnalysisApp:
    """Main application class that orchestrates UI and Agent logic"""
    
    def __init__(self):
        """Initialize the application"""
        self.agent = None
        self.analysis_results = None
        self.initialize_session_state()
    
    def initialize_session_state(self):
        """Initialize Streamlit session state variables"""
        if "agent" not in st.session_state:
            st.session_state.agent = None
        
        if "analysis_results" not in st.session_state:
            st.session_state.analysis_results = None
        
        if "analysis_complete" not in st.session_state:
            st.session_state.analysis_complete = False
        
        if "error_message" not in st.session_state:
            st.session_state.error_message = None

    def initialize_agent(self, cutoff_score=75):
        """Initialize the Resume Analysis Agent with API key from environment"""
        try:
            # Get API key from environment variable
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError(
                    "OpenAI API Key not found. Please set OPENAI_API_KEY environment variable. "
                    "You can also add it directly in the code by modifying config.py"
                )
            
            agent = ResumeAnalysisAgent(api_key=api_key, cutoff_score=cutoff_score)
            st.session_state.agent = agent
            self.agent = agent
            return True
        except Exception as e:
            st.session_state.error_message = f"Failed to initialize agent: {str(e)}"
            return False

    def validate_inputs(self, resume_file, jd_file, role_requirements_text):
        """Validate user inputs"""
        if not resume_file:
            return False, "Please upload a resume file"
        
        if not jd_file and not role_requirements_text:
            return False, "Please either upload a job description or specify role requirements"
        
        if jd_file:
            # Validate file type
            if not jd_file.name.lower().endswith(('.pdf', '.txt')):
                return False, "Job description must be PDF or TXT format"
        
        return True, "Inputs are valid"

    def process_role_requirements(self, requirements_text):
        """Process role requirements from text input"""
        if not requirements_text:
            return []
        
        skills = [skill.strip() for skill in requirements_text.split(",")]
        skills = [s for s in skills if s]  # Remove empty strings
        return skills

    def analyze_resume(self, resume_file, jd_file=None, role_requirements=None):
        """Execute resume analysis"""
        try:
            # Get agent from session state if not available in self
            agent = self.agent if self.agent else st.session_state.agent
            if not agent:
                return False, "Agent not initialized. Please enter your OpenAI API Key."
            
            # Create a custom file object if we have a jd_file
            analysis_results = agent.analyze_resume(
                resume_file=resume_file,
                custom_jd=jd_file,
                role_requirements=role_requirements
            )
            
            if analysis_results:
                st.session_state.analysis_results = analysis_results
                st.session_state.analysis_complete = True
                return True, analysis_results
            else:
                return False, "Analysis failed to produce results"
        
        except Exception as e:
            error_msg = str(e)
            # Encode error message safely as UTF-8
            if isinstance(error_msg, bytes):
                error_msg = error_msg.decode('utf-8', errors='replace')
            # Remove any problematic characters
            error_msg = error_msg.encode('utf-8', errors='replace').decode('utf-8', errors='replace')
            error_msg = f"Error during analysis: {error_msg}"
            st.session_state.error_message = error_msg
            return False, error_msg
    
    def clear_faiss_cache(self):
        """Clear FAISS index cache to ensure fresh analysis"""
        try:
            import shutil
            faiss_dir = 'faiss_indexes'
            if os.path.exists(faiss_dir):
                shutil.rmtree(faiss_dir)
                print(f"Cleared FAISS cache directory: {faiss_dir}")
        except Exception as e:
            print(f"Error clearing FAISS cache: {e}")

    def render_main_content(self):
        """Render the main application content"""
        # Render header
        ResumeAnalysisUI.render_header()
        
        # Render sidebar and get configuration
        cutoff_score = ResumeAnalysisUI.render_sidebar()
        
        # Initialize agent with API key from environment
        if st.session_state.agent is None:
            self.initialize_agent(cutoff_score)
        
        self.agent = st.session_state.agent
        
        if not self.agent or st.session_state.agent is None:
            ResumeAnalysisUI.render_warning(st.session_state.error_message or "Failed to initialize. Please check your OpenAI API Key configuration.")
            return
        
        # Main content area
        main_col1, main_col2 = st.columns([2, 1])
        
        with main_col1:
            # File upload section
            resume_file, jd_file = ResumeAnalysisUI.render_file_upload_section()
            
            # Alternative: role requirements section
            role_requirements_text = ResumeAnalysisUI.render_role_requirements_section()
            
            # Validate inputs
            is_valid, validation_message = self.validate_inputs(
                resume_file, 
                jd_file, 
                role_requirements_text
            )
            
            if not is_valid and (resume_file or jd_file or role_requirements_text):
                ResumeAnalysisUI.render_warning(validation_message)
            
            # Analysis section
            analyze_button, clear_button, reset_button = ResumeAnalysisUI.render_analysis_section()
            
            # Handle reset button click - Clear everything including FAISS cache
            if reset_button:
                st.session_state.analysis_results = None
                st.session_state.analysis_complete = False
                st.session_state.error_message = None
                # Clear FAISS indexes
                self.clear_faiss_cache()
                st.success("All caches cleared! Ready for fresh analysis.")
                st.rerun()
            
            # Handle analysis button click
            if analyze_button:
                if not is_valid:
                    ResumeAnalysisUI.render_error(validation_message)
                else:
                    with st.spinner("🔄 Analyzing resume... This may take a minute..."):
                        # Process role requirements if provided
                        role_requirements = None
                        if role_requirements_text and not jd_file:
                            role_requirements = self.process_role_requirements(role_requirements_text)
                        
                        # Run analysis
                        success, result = self.analyze_resume(
                            resume_file,
                            jd_file=jd_file,
                            role_requirements=role_requirements
                        )
                        
                        if success:
                            ResumeAnalysisUI.render_success("Analysis completed successfully!")
                        else:
                            ResumeAnalysisUI.render_error(result)
            
            # Handle clear button click
            if clear_button:
                st.session_state.analysis_results = None
                st.session_state.analysis_complete = False
                st.rerun()
        
        with main_col1:
            # Display results if analysis is complete
            if st.session_state.analysis_complete and st.session_state.analysis_results:
                st.divider()
                self.render_analysis_results(st.session_state.analysis_results)

    def render_analysis_results(self, results):
        """Render comprehensive analysis results"""
        st.header("📊 Analysis Results")
        
        # Results header with score and status
        ResumeAnalysisUI.render_results_header(
            results.get("overall_score", 0),
            results.get("selected", False)
        )
        
        st.divider()
        
        # Skill analysis
        if results.get("skill_scores"):
            ResumeAnalysisUI.render_skill_scores(
                results.get("skill_scores", {}),
                results.get("skill_reasonings", {})
            )
            st.divider()
        
        # Strengths
        if results.get("strengths"):
            ResumeAnalysisUI.render_strengths(results.get("strengths", []))
            st.divider()
        
        # Weaknesses with improvements
        if results.get("resume_weaknesses"):
            ResumeAnalysisUI.render_weaknesses(results.get("resume_weaknesses", []))
            st.divider()
        
        # Improvement areas
        ResumeAnalysisUI.render_improvement_areas(results.get("missing_skills", []))
        st.divider()
        
        # Analysis reasoning
        ResumeAnalysisUI.render_reasoning(results.get("reasoning", ""))
        st.divider()
        
        # Export results
        ResumeAnalysisUI.render_export_results(results)

    def run(self):
        """Run the application"""
        self.render_main_content()
        
        # Display any error messages
        if st.session_state.error_message:
            ResumeAnalysisUI.render_error(st.session_state.error_message)


def main():
    """Main entry point for the Streamlit application"""
    app = ResumeAnalysisApp()
    app.run()


if __name__ == "__main__":
    main()
