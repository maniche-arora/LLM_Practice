import streamlit as st
import json
from datetime import datetime


class ResumeAnalysisUI:
    """UI Components for Resume Analysis Application"""
    
    @staticmethod
    def render_header():
        """Render the application header"""
        st.set_page_config(
            page_title="Resume AI Analyzer",
            page_icon="📄",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("# 📄 Resume AI Analyzer")
            st.markdown("*Intelligent Resume Analysis Against Job Requirements*")
        
        st.divider()

    @staticmethod
    def render_sidebar():
        """Render sidebar with configuration options"""
        with st.sidebar:
            st.header("⚙️ Configuration")
            
            cutoff_score = st.slider(
                "Selection Cutoff Score",
                min_value=0,
                max_value=100,
                value=75,
                step=5,
                help="Minimum score for candidate selection"
            )
            
            st.divider()
            st.markdown("### About")
            st.info(
                "This tool analyzes resumes against job descriptions or role requirements "
                "using AI-powered semantic analysis to identify strengths, weaknesses, "
                "and improvement opportunities."
            )
            
            return cutoff_score

    @staticmethod
    def render_file_upload_section():
        """Render file upload section for resume and job description"""
        st.header("📤 Upload Documents")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Resume")
            resume_file = st.file_uploader(
                "Upload your resume (PDF or TXT)",
                type=["pdf", "txt"],
                key="resume_upload",
                help="Supported formats: PDF or TXT"
            )
        
        with col2:
            st.subheader("Job Description")
            jd_file = st.file_uploader(
                "Upload job description (PDF or TXT)",
                type=["pdf", "txt"],
                key="jd_upload",
                help="Supported formats: PDF or TXT"
            )
        
        st.divider()
        
        return resume_file, jd_file

    @staticmethod
    def render_role_requirements_section():
        """Render alternative section for manual role requirements"""
        st.header("🎯 Or Specify Role Requirements")
        
        requirements_text = st.text_area(
            "Enter role requirements (comma-separated skills)",
            placeholder="e.g., Python, Machine Learning, Data Analysis, SQL, TensorFlow",
            height=100,
            help="Enter skills/requirements separated by commas"
        )
        
        if requirements_text:
            skills = [skill.strip() for skill in requirements_text.split(",") if skill.strip()]
            if skills:
                st.success(f"✓ {len(skills)} skills identified")
                st.write("**Skills to analyze:**")
                cols = st.columns(3)
                for idx, skill in enumerate(skills):
                    with cols[idx % 3]:
                        st.write(f"• {skill}")
        
        st.divider()
        
        return requirements_text

    @staticmethod
    def render_analysis_section():
        """Render analysis button and loading states"""
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            analyze_button = st.button(
                "🔍 Analyze Resume",
                use_container_width=True,
                type="primary"
            )
        
        with col2:
            clear_button = st.button(
                "🔄 Clear Results",
                use_container_width=True
            )
        
        with col3:
            reset_button = st.button(
                "⚡ Reset All",
                use_container_width=True,
                help="Clear all caches and start fresh"
            )
        
        return analyze_button, clear_button, reset_button

    @staticmethod
    def render_results_header(overall_score, selected):
        """Render results header with overall score and selection status"""
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            st.metric(
                "Overall Score",
                f"{overall_score}%",
                delta=None,
                delta_color="normal"
            )
        
        with col2:
            status = "[RECOMMENDED]" if selected else "[NOT RECOMMENDED]"
            st.metric(
                "Selection Status",
                status
            )
        
        with col3:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            st.metric(
                "Analysis Date",
                timestamp
            )

    @staticmethod
    def render_skill_scores(skill_scores, skill_reasonings):
        """Render skill scores in a detailed table"""
        st.subheader("📊 Skill Analysis")
        
        # Create data for display
        skill_data = []
        for skill, score in skill_scores.items():
            reasoning = skill_reasonings.get(skill, "No explanation provided")
            skill_data.append({
                "Skill": skill,
                "Score": score * 10,  # Convert to percentage
                "Assessment": reasoning
            })
        
        # Sort by score descending
        skill_data.sort(key=lambda x: x["Score"], reverse=True)
        
        # Display skills with color coding
        for item in skill_data:
            col1, col2, col3 = st.columns([2, 1, 4])
            
            with col1:
                st.write(f"**{item['Skill']}**")
            
            with col2:
                score_pct = item['Score']
                if score_pct >= 70:
                    st.success(f"{score_pct}%")
                elif score_pct >= 40:
                    st.warning(f"{score_pct}%")
                else:
                    st.error(f"{score_pct}%")
            
            with col3:
                st.caption(item['Assessment'])

    @staticmethod
    def render_strengths(strengths):
        """Render identified strengths"""
        st.subheader("💪 Identified Strengths")
        
        if strengths:
            cols = st.columns(min(3, len(strengths)))
            for idx, strength in enumerate(strengths):
                with cols[idx % 3]:
                    st.success(f"✓ {strength}", icon="✅")
        else:
            st.info("No strong skills identified based on the analysis.")

    @staticmethod
    def render_weaknesses(weaknesses):
        """Render identified weaknesses with improvement suggestions"""
        st.subheader("⚠️ Areas for Improvement")
        
        if weaknesses:
            for idx, weakness in enumerate(weaknesses, 1):
                with st.expander(
                    f"🔴 {weakness['skill']} (Score: {weakness.get('score', 0) * 10}%)",
                    expanded=(idx == 1)
                ):
                    st.markdown(f"**Issue:** {weakness.get('detail', 'N/A')}")
                    
                    suggestions = weakness.get('suggestions', [])
                    if suggestions:
                        st.markdown("**Improvement Suggestions:**")
                        for i, suggestion in enumerate(suggestions, 1):
                            st.write(f"{i}. {suggestion}")
                    
                    example = weakness.get('example', '')
                    if example:
                        st.markdown("**Example Addition:**")
                        with st.container(border=True):
                            st.write(f"*{example}*")
        else:
            st.success("✓ No major weaknesses detected!", icon="✅")

    @staticmethod
    def render_improvement_areas(improvement_areas):
        """Render overall improvement areas"""
        if improvement_areas:
            st.subheader("🎯 Recommended Improvement Areas")
            
            cols = st.columns(2)
            for idx, area in enumerate(improvement_areas):
                with cols[idx % 2]:
                    st.warning(f"• {area}")
        else:
            st.success("✓ Resume aligns well with role requirements!")

    @staticmethod
    def render_reasoning(reasoning):
        """Render analysis reasoning"""
        st.subheader("📋 Analysis Methodology")
        with st.container(border=True):
            st.write(reasoning)

    @staticmethod
    def render_error(error_message):
        """Render error message"""
        st.error(f"ERROR: {error_message}")

    @staticmethod
    def render_warning(warning_message):
        """Render warning message"""
        st.warning(f"⚠️ {warning_message}")

    @staticmethod
    def render_success(success_message):
        """Render success message"""
        st.success(f"✅ {success_message}")

    @staticmethod
    def render_loading_state(message="Processing..."):
        """Render loading state"""
        with st.spinner(message):
            st.write("⏳ Please wait...")

    @staticmethod
    def render_export_results(analysis_results):
        """Render export options for results"""
        st.subheader("📥 Export Results")
        
        col1, col2 = st.columns(2)
        
        with col1:
            json_str = json.dumps(analysis_results, indent=2)
            st.download_button(
                label="📄 Download as JSON",
                data=json_str,
                file_name=f"resume_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
        
        with col2:
            # Create a formatted text version
            text_report = ResumeAnalysisUI._format_report_as_text(analysis_results)
            st.download_button(
                label="📝 Download as Text",
                data=text_report,
                file_name=f"resume_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True
            )

    @staticmethod
    def _format_report_as_text(analysis_results):
        """Format analysis results as readable text report"""
        report = "=" * 80 + "\n"
        report += "RESUME ANALYSIS REPORT\n"
        report += "=" * 80 + "\n\n"
        
        report += f"Overall Score: {analysis_results.get('overall_score', 'N/A')}%\n"
        report += f"Selection Status: {'RECOMMENDED' if analysis_results.get('selected') else 'NOT RECOMMENDED'}\n"
        report += f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        report += "-" * 80 + "\n"
        report += "SKILL SCORES\n"
        report += "-" * 80 + "\n"
        for skill, score in analysis_results.get('skill_scores', {}).items():
            report += f"• {skill}: {score * 10}%\n"
        
        report += "\n" + "-" * 80 + "\n"
        report += "STRENGTHS\n"
        report += "-" * 80 + "\n"
        for strength in analysis_results.get('strengths', []):
            report += f"✓ {strength}\n"
        
        if analysis_results.get('resume_weaknesses'):
            report += "\n" + "-" * 80 + "\n"
            report += "AREAS FOR IMPROVEMENT\n"
            report += "-" * 80 + "\n"
            for weakness in analysis_results.get('resume_weaknesses', []):
                report += f"\n• {weakness.get('skill', 'N/A')}\n"
                report += f"  Issue: {weakness.get('detail', 'N/A')}\n"
                for suggestion in weakness.get('suggestions', []):
                    report += f"  - {suggestion}\n"
        
        return report
