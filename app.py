"""
Streamlit Application for DNA Sequence Analysis
FIXED: KeyError for donor_position
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import base64
import re
import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from dna_analyzer_advanced import AdvancedDNAAnalyzer
    ANALYZER_AVAILABLE = True
except ImportError:
    ANALYZER_AVAILABLE = False
    st.error("❌ dna_analyzer_advanced.py not found. Please create it in the same directory.")


st.set_page_config(
    page_title="🧬 DNA Sequence Analyzer",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)



def load_css():
    """Load custom CSS styles"""
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #2E86AB;
        font-weight: 700;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #A23B72;
        font-weight: 600;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    .card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border-left: 5px solid #2E86AB;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .stButton > button {
        background-color: #2E86AB;
        color: white;
        border: none;
        padding: 0.5rem 1.5rem;
        border-radius: 5px;
        font-weight: 600;
    }
    .stButton > button:hover {
        background-color: #1C6B8C;
    }
    .sequence-display {
        font-family: 'Courier New', monospace;
        background-color: #2D3047;
        color: #FFFFFF;
        padding: 1rem;
        border-radius: 5px;
        overflow-x: auto;
        white-space: pre-wrap;
        font-size: 0.9rem;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

def create_download_link(df, filename, text):
    """Generate a download link for DataFrame"""
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'
    return href

def format_sequence(sequence, width=80):
    """Format DNA sequence for display"""
    formatted = []
    for i in range(0, len(sequence), width):
        chunk = sequence[i:i+width]
        line_num = f"{i:5d}  "
        formatted.append(f"{line_num}{chunk}")
    return "\n".join(formatted)



def create_sidebar():
    """Create the sidebar with configuration options"""
    with st.sidebar:
        st.title("⚙️ Configuration")
        
    
        model_option = st.selectbox(
            "Select Model",
            ["Random Forest", "Gradient Boosting", "Neural Network"],
            index=0
        )
        
        st.subheader("Sequence Settings")
        min_length = st.number_input(
            "Minimum Sequence Length", 
            min_value=50, 
            max_value=1000, 
            value=100,
            help="Minimum length for sequence analysis"
        )
        
    
        st.subheader("🧪 Sample Sequences")
        sample_option = st.selectbox(
            "Choose Sample Sequence",
            [
                "Human BRCA1 Exon",
                "Mouse Insulin Intron", 
                "HIV-1 Donor Site",
                "E. coli Promoter",
                "Random Synthetic DNA"
            ],
            index=0
        )
        
        if st.button("Load Sample"):
        
            samples = {
                "Human BRCA1 Exon": "ATGGATTTATCTGCTCTTCGCGTTGAAGAAGTACAAAATGTCATTAATGCTATGCAGAAAATCTTAGAGTGTCCCATCTGTCTGGAGTTGATCAAGGAACCTGTCTCCACAAAGTGTGACCACATATTTTGCAAATTTTGCATGCTGAAACTTCTCAACCAGAAGAAAGGGCCTTCACAGTGTCCTTTATGTAAGAATGATATAACCAAAAGGAGCCTACAAGAAAGTACGAGATTTAGTCAACTTGTTGAAGAGCTATTGAAAATCATTTGTGCTTTTCAGCTTGACACAGGTTTGGAGTATGCAAACAGCTATAATTTTGCAAAAAAGGAAAATAACTCTCCTGAACATCTAAAAGATGAAGTTTCTATCATCCAAAGTATGGGCTACAGAAACCGTGCCAAAAGACTTCTACAGAGTGAACCCGAAAATCCTTCCTTGCAGGAAACCAGTCTCAGTGTCCAACTCTCTAACCTTGGAACTGTGAGAACTCTGAGGACAAAGCAGCGGATACAACCTCAAAAGACGTCTGTCTACATTGAATTGGGATCTGATTCTTCTGAAGATACCGTTAATAAGGCAACTTATTGCAGTGTGGGAGATCAAGAATTGTTACAAATCACCCCTCAAGGAACCAGGGATGAAATCAGTTTGGATTCTGCAAAAAAGCTGCTTGTACATCCAAACTGATGAGTCTGA",
                "Mouse Insulin Intron": "GTATTTTCTTTTCCCCAGCTGCTCTGCCTCTGCCCGAGGTCTGCAGCACCATGGCCCTGTGGATGCGCCTCCTGCCCCTGCTGGCGCTGCTGGCCCTCTGGGGACCTGACCCAGCCGCAGCCTTTGTGAACCAACACCTGTGCGGCTCACACCTGGTGGAAGCTCTCTACCTAGTGTGCGGGGAACGAGGCTTCTTCTACACACCCAAGACCCGCCGGGAGGCAGAGGACCTGCAGGTGGGGCAGGTGGAGCTGGGCGGGGGCCCTGGTGCAGGCAGCCTGCAGCCCTTGGCCCTGGAGGGGTCCCTGCAGAAGCGTGGCATTGTGGAACAATGCTGTACCAGCATCTGCTCCCTCTACCAGCTGGAGAACTACTGCAACTA",
                "HIV-1 Donor Site": "CCTGGGTTGTGGAAAATCTCTAGCAGTGGCGCCCGAACAGGGACTTGAAAGCGAAAGGGAAACCAGAGGAGCTCTCTCGACGCAGGACTCGGCTTGCTGAAGCGCGCACGGCAAGAGGCGAGGGGCGGCGACTGGTGAGTACGCCAAAAATTTTGACTAGCGGAGGCTAGAAGGAGAGAGATGGGTGCGAGAGCGTCAGTATTAAGCGGGGGAGAATTAGATCGATGGGAAAAAATTCGGTTAAGGCCAGGGGGAAAGAAAAAATATAAATTAAAACATATAGTATGGGCAAGCAGGGAGCTAGAACGATTCGCAGTTAATCCTGGCCTGTTAGAAACATCAGAAGGCTGTAGACAAATACTGGGACAGCTACAACCATCCCTTCAGACAGGATCAGAAGAACTTAGATCATTATATAATACAGTAGCAACCCTCTATTGTGTGCATCAAAGGATAGAGATAAAAGACACCAAGGAAGCTTTAGACAAGATAGAGGAAGAGCAAAACAAAAGTAAG",
                "E. coli Promoter": "TTGACAATTAATCATCGGCTCGTATAATGTGTGGAATTGTGAGCGGATAACAATTTCACACAGGAAACAGCTATGACCATGATTACGAATTCGAGCTCGGTACCCGGGGATCCTCTAGAGTCGACCTGCAGGCATGCAAGCTTGGCACTGGCCGTCGTTTTACAACGTCGTGACTGGGAAAACCCTGGCGTTACCCAACTTAATCGCCTTGCAGCACATCCCCCTTTCGCCAGCTGGCGTAATAGCGAAGAGGCCCGCACCGATCGCCCTTCCCAACAGTTGCGCAGCCTGAATGGCGAATGG",
                "Random Synthetic DNA": "".join(np.random.choice(['A', 'C', 'G', 'T'], 300))
            }
            
            selected_seq = samples[sample_option]
            st.session_state['input_sequence'] = selected_seq
            st.success(f"✅ Loaded {sample_option} sample!")
            st.rerun()
        
        # Information
        st.markdown("---")
        st.markdown("### 📊 Application Info")
        st.markdown("**Version:** 2.0.0")
        st.markdown("**Author:** DNA Analyzer Team")
        st.markdown("**License:** MIT")


def main():
    """Main application function"""

    load_css()
    
    if 'analyzer' not in st.session_state and ANALYZER_AVAILABLE:
        st.session_state['analyzer'] = AdvancedDNAAnalyzer()
    
    if 'analysis_results' not in st.session_state:
        st.session_state['analysis_results'] = None
    
    if 'input_sequence' not in st.session_state:
        st.session_state['input_sequence'] = ""
    
    st.markdown('<h1 class="main-header">🧬 DNA Sequence Analyzer</h1>', unsafe_allow_html=True)
    st.markdown("Analyze any DNA sequence for exons, introns, and splice junctions")
    
    create_sidebar()
    
    tab1, tab2, tab3 = st.tabs(["🏠 Analyze", "📊 Results", "⚙️ Settings"])
    
    with tab1:
        st.markdown('<div class="sub-header">🔬 DNA Sequence Input</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            sequence_input = st.text_area(
                "Enter DNA Sequence (ACGT only):",
                value=st.session_state['input_sequence'],
                height=200,
                placeholder="Paste your DNA sequence here...\nExample: ATGCTAGCTAGCTAGCTAGC...",
                help="Enter a DNA sequence for analysis. Minimum 50 bases recommended."
            )
        
        with col2:
            st.markdown("""
            <div class="card">
            <h4>📝 Input Tips</h4>
            <ul>
            <li>Use only A, C, G, T characters</li>
            <li>Remove spaces and line breaks</li>
            <li>Minimum 50 bases</li>
            <li>200+ bases for better results</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)
        

        col1, col2, col3 = st.columns(3)
        
        with col1:
            analyze_btn = st.button("🚀 Analyze Sequence", type="primary", use_container_width=True)
        
        with col2:
            clear_btn = st.button("🗑️ Clear", use_container_width=True)
        
        with col3:
            example_seq = "ATGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCGTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAG"
            example_btn = st.button("📚 Load Example", use_container_width=True)
        
        if clear_btn:
            st.session_state['input_sequence'] = ""
            st.session_state['analysis_results'] = None
            st.rerun()
        
        if example_btn:
            st.session_state['input_sequence'] = example_seq
            st.rerun()
    
        if analyze_btn and sequence_input:
        
            seq_clean = sequence_input.upper().replace(" ", "").replace("\n", "")
            
        
            valid_chars = set('ACGTN')
            if not set(seq_clean).issubset(valid_chars):
                st.error("❌ Invalid characters detected. Use only A, C, G, T, N.")
            elif len(seq_clean) < 50:
                st.warning(f"⚠️ Sequence too short ({len(seq_clean)} bases). Minimum 50 bases recommended.")
            else:
                st.success(f"✅ Valid sequence: {len(seq_clean)} bases")
                
                if ANALYZER_AVAILABLE:
                    with st.spinner("🔬 Analyzing sequence..."):
                        try:
                        
                            st.session_state['input_sequence'] = seq_clean
                            
                        
                            analyzer = st.session_state['analyzer']
                            results = analyzer.analyze_sequence(seq_clean)
                            st.session_state['analysis_results'] = results
                            
                            st.success("✅ Analysis complete!")
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"❌ Analysis error: {str(e)}")
                else:
                    st.error("❌ Analyzer not available. Please create dna_analyzer_advanced.py")
    

    with tab2:
        if st.session_state.get('analysis_results'):
            results = st.session_state['analysis_results']
            
            if 'error' in results:
                st.error(f"Analysis error: {results['error']}")
            else:
            
                st.markdown('<div class="sub-header">📋 Analysis Results</div>', unsafe_allow_html=True)
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Sequence Length", f"{results['length']} bp")
                
                with col2:
                    st.metric("Prediction", results['overall_prediction'])
                
                with col3:
                    st.metric("Confidence", f"{results['overall_confidence']:.1f}%")
                
                with col4:
                    st.metric("GC Content", f"{results.get('gc_content', 0):.1f}%")
                
    
                st.markdown("### 🧬 Sequence Preview")
                seq_preview = st.session_state['input_sequence'][:200] + "..." if len(st.session_state['input_sequence']) > 200 else st.session_state['input_sequence']
                st.code(format_sequence(seq_preview, 50), language=None)
        
                with st.expander("📊 Detailed Prediction Probabilities"):
                    if 'class_probabilities' in results:
                        prob_df = pd.DataFrame({
                            'Class': list(results['class_probabilities'].keys()),
                            'Probability (%)': list(results['class_probabilities'].values())
                        })
                        prob_df = prob_df.sort_values('Probability (%)', ascending=False)
                
                        fig = px.bar(
                            prob_df,
                            x='Class',
                            y='Probability (%)',
                            color='Probability (%)',
                            color_continuous_scale='Viridis',
                            title="Prediction Probabilities"
                        )
                        fig.update_traces(texttemplate='%{y:.1f}%', textposition='outside')
                        fig.update_layout(height=400)
                        st.plotly_chart(fig, use_container_width=True)
            
                with st.expander("🔗 Splice Junctions"):
                    if 'splice_junctions' in results:
                        junctions = results['splice_junctions']
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("**Donor Sites (GT):**")
                            if junctions.get('donor_sites'):
                                donor_sites = junctions['donor_sites']
                                if isinstance(donor_sites, list) and len(donor_sites) > 0:
            
                                    for i, site in enumerate(donor_sites[:5]):
                                        if isinstance(site, dict):
                                           
                                            pos = site.get('position', 'N/A')
                                            context = site.get('context', '')
                                            st.write(f"{i+1}. Position {pos}: {context}")
                                        elif isinstance(site, int):
                                          
                                            st.write(f"{i+1}. Position {site}")
                                        else:
                                            st.write(f"{i+1}. {site}")
                                else:
                                    st.write("No donor sites found")
                            else:
                                st.write("No donor sites found")
                        
                        with col2:
                            st.markdown("**Acceptor Sites (AG):**")
                            if junctions.get('acceptor_sites'):
                                acceptor_sites = junctions['acceptor_sites']
                                if isinstance(acceptor_sites, list) and len(acceptor_sites) > 0:
                                    for i, site in enumerate(acceptor_sites[:5]):
                                        if isinstance(site, dict):
                                            pos = site.get('position', 'N/A')
                                            context = site.get('context', '')
                                            st.write(f"{i+1}. Position {pos}: {context}")
                                        elif isinstance(site, int):
                                            st.write(f"{i+1}. Position {site}")
                                        else:
                                            st.write(f"{i+1}. {site}")
                                else:
                                    st.write("No acceptor sites found")
                            else:
                                st.write("No acceptor sites found")
                    
                        if junctions.get('intron_boundaries'):
                            st.markdown("**Potential Intron Boundaries:**")
                            boundaries = junctions['intron_boundaries']
                            if isinstance(boundaries, list):
                                for i, boundary in enumerate(boundaries[:3]):
                                
                                    if isinstance(boundary, dict):
                                        donor_key = None
                                        acceptor_key = None
                                    
                                        possible_donor_keys = ['donor_position', 'donor', 'donor_site', 'gt_position']
                                        possible_acceptor_keys = ['acceptor_position', 'acceptor', 'acceptor_site', 'ag_position']
                                        
                                        for key in possible_donor_keys:
                                            if key in boundary:
                                                donor_key = key
                                                break
                                        
                                        for key in possible_acceptor_keys:
                                            if key in boundary:
                                                acceptor_key = key
                                                break
                                        
                                        if donor_key and acceptor_key:
                                            donor_pos = boundary.get(donor_key, 'N/A')
                                            acceptor_pos = boundary.get(acceptor_key, 'N/A')
                                            distance = boundary.get('distance', 'N/A')
                                            st.write(f"{i+1}. Donor {donor_pos} to Acceptor {acceptor_pos} (Distance: {distance} bp)")
                                        else:
                                           
                                            st.write(f"{i+1}. Boundary data: {boundary}")
                                    else:
                                        st.write(f"{i+1}. {boundary}")
                        else:
                       
                            st.markdown("**Finding GT-AG pairs...**")
                            seq = st.session_state.get('input_sequence', '')
                            if seq:
                               
                                gt_positions = [m.start() for m in re.finditer('GT', seq)]
                                ag_positions = [m.start() for m in re.finditer('AG', seq)]
                                
                              
                                pairs_found = 0
                                for gt in gt_positions[:10]:
                                    for ag in ag_positions[:10]:
                                        if ag > gt + 10: 
                                            distance = ag - gt
                                            st.write(f"- GT at {gt} → AG at {ag} (Distance: {distance} bp)")
                                            pairs_found += 1
                                            if pairs_found >= 3:
                                                break
                                    if pairs_found >= 3:
                                        break
                                
                                if pairs_found == 0:
                                    st.write("No GT-AG pairs found")
            
                with st.expander("📊 Base Composition"):
                    if 'base_composition' in results:
                        bases = ['A', 'C', 'G', 'T']
                        percentages = [results['base_composition'].get(base, 0) for base in bases]
                        
                        fig = px.pie(
                            values=percentages,
                            names=bases,
                            color=bases,
                            color_discrete_map={'A': '#FF6B6B', 'C': '#4ECDC4', 'G': '#45B7D1', 'T': '#96CEB4'},
                            title="Base Composition"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        seq = st.session_state.get('input_sequence', '')
                        if seq:
                            length = len(seq)
                            bases = ['A', 'C', 'G', 'T']
                            percentages = [seq.count(base) / length * 100 for base in bases]
                            
                            fig = px.pie(
                                values=percentages,
                                names=bases,
                                color=bases,
                                color_discrete_map={'A': '#FF6B6B', 'C': '#4ECDC4', 'G': '#45B7D1', 'T': '#96CEB4'},
                                title="Base Composition"
                            )
                            st.plotly_chart(fig, use_container_width=True)
                
    
                st.markdown("---")
                st.subheader("📥 Download Results")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("Export Summary as CSV", use_container_width=True):
            
                        result_data = {
                            'sequence_length': results.get('length', 0),
                            'prediction': results.get('overall_prediction', 'unknown'),
                            'confidence': results.get('overall_confidence', 0),
                            'gc_content': results.get('gc_content', 0),
                            'donor_sites': results.get('donor_site_count', 0),
                            'acceptor_sites': results.get('acceptor_site_count', 0),
                            'has_start_codon': results.get('has_start_codon', 0),
                            'has_stop_codon': results.get('has_stop_codon', 0)
                        }
                        
                        df = pd.DataFrame([result_data])
                        csv = df.to_csv(index=False)
                        b64 = base64.b64encode(csv.encode()).decode()
                        href = f'<a href="data:file/csv;base64,{b64}" download="dna_analysis.csv">Download CSV</a>'
                        st.markdown(href, unsafe_allow_html=True)
                
                with col2:
                    if st.button("Export Full Data", use_container_width=True):
                        st.info("Full data export coming soon!")
        
        else:
            st.info("ℹ️ No analysis results yet. Please analyze a sequence in the 'Analyze' tab.")
    
    with tab3:
        st.markdown('<div class="sub-header">⚙️ Settings</div>', unsafe_allow_html=True)
        
        if not ANALYZER_AVAILABLE:
            st.error("""
            ❌ dna_analyzer_advanced.py not found in the current directory.
            
            Please create a file named `dna_analyzer_advanced.py` in the same folder as `app.py`
            with the DNA analyzer class code.
            """)
        
        st.markdown("### Application Settings")
    
        if ANALYZER_AVAILABLE and 'analyzer' in st.session_state:
            if st.button("🔄 Train New Model", use_container_width=True):
                with st.spinner("Training model..."):
                    try:
                        analyzer = st.session_state['analyzer']
                        metrics = analyzer.train_model()
                        st.success(f"✅ Model trained! Accuracy: {metrics['test_accuracy']*100:.1f}%")
                    except Exception as e:
                        st.error(f"❌ Training failed: {str(e)}")
        
    
        st.markdown("---")
        st.markdown("### 📖 About")
        st.markdown("""
        **DNA Sequence Analyzer** v2.0.0
        
        This application analyzes DNA sequences to identify:
        - 🧬 **Exons**: Protein-coding regions
        - 🧬 **Introns**: Non-coding regions  
        - 🧬 **Splice Junctions**: Donor (GT) and Acceptor (AG) sites
        
        **Features:**
        - Analyze sequences of any length
        - Machine learning classification
        - Detailed feature extraction
        - Interactive visualizations
        - Export results
        
        **Requirements:**
        - Python 3.8+
        - Streamlit
        - Scikit-learn
        - NumPy, Pandas
        - Plotly
        """)


if __name__ == "__main__":
    main()