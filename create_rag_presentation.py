from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
import os

def create_rag_presentation():
    """Create a simple RAG explanation PowerPoint presentation."""
    
    prs = Presentation()
    prs.slide_width = Inches(10)
    prs.slide_height = Inches(7.5)
    
    # Define color scheme
    DARK_BLUE = RGBColor(31, 78, 121)
    LIGHT_BLUE = RGBColor(79, 129, 189)
    ACCENT = RGBColor(192, 0, 0)
    DARK_TEXT = RGBColor(51, 51, 51)
    
    def add_title_slide(title, subtitle=""):
        """Add a title slide."""
        slide = prs.slides.add_slide(prs.slide_layouts[6])  # Blank layout
        background = slide.background
        fill = background.fill
        fill.solid()
        fill.fore_color.rgb = DARK_BLUE
        
        # Title
        title_box = slide.shapes.add_textbox(Inches(0.5), Inches(2.5), Inches(9), Inches(1.5))
        title_frame = title_box.text_frame
        title_frame.word_wrap = True
        p = title_frame.paragraphs[0]
        p.text = title
        p.font.size = Pt(54)
        p.font.bold = True
        p.font.color.rgb = RGBColor(255, 255, 255)
        p.alignment = PP_ALIGN.CENTER
        
        # Subtitle
        if subtitle:
            subtitle_box = slide.shapes.add_textbox(Inches(0.5), Inches(4.2), Inches(9), Inches(1))
            subtitle_frame = subtitle_box.text_frame
            p = subtitle_frame.paragraphs[0]
            p.text = subtitle
            p.font.size = Pt(28)
            p.font.color.rgb = LIGHT_BLUE
            p.alignment = PP_ALIGN.CENTER
    
    def add_content_slide(title, content_points):
        """Add a content slide with bullet points."""
        slide = prs.slides.add_slide(prs.slide_layouts[6])  # Blank layout
        background = slide.background
        fill = background.fill
        fill.solid()
        fill.fore_color.rgb = RGBColor(242, 242, 242)
        
        # Title bar
        title_shape = slide.shapes.add_shape(1, Inches(0), Inches(0), Inches(10), Inches(1))
        title_shape.fill.solid()
        title_shape.fill.fore_color.rgb = DARK_BLUE
        title_shape.line.color.rgb = DARK_BLUE
        
        # Title text
        title_frame = title_shape.text_frame
        title_frame.clear()
        p = title_frame.paragraphs[0]
        p.text = title
        p.font.size = Pt(40)
        p.font.bold = True
        p.font.color.rgb = RGBColor(255, 255, 255)
        p.space_before = Pt(10)
        p.space_after = Pt(10)
        
        # Content
        left = Inches(0.75)
        top = Inches(1.5)
        width = Inches(8.5)
        height = Inches(5.5)
        
        text_box = slide.shapes.add_textbox(left, top, width, height)
        text_frame = text_box.text_frame
        text_frame.word_wrap = True
        
        for i, point in enumerate(content_points):
            if i == 0:
                p = text_frame.paragraphs[0]
            else:
                p = text_frame.add_paragraph()
            
            p.text = point
            p.font.size = Pt(24)
            p.font.color.rgb = DARK_TEXT
            p.level = 0
            p.space_before = Pt(8)
            p.space_after = Pt(8)
            p.line_spacing = 1.3
    
    # Slide 1: Title
    add_title_slide("RAG", "Retrieval-Augmented Generation")
    
    # Slide 2: What is RAG?
    add_content_slide("What is RAG?", [
        "🔍 Retrieval: Finding relevant documents/code from a database",
        "💬 Augmented: Enhancing the LLM with external context",
        "🧠 Generation: Using LLM to produce answers based on retrieved context",
        "",
        "Problem it solves: LLMs have outdated training data and can hallucinate"
    ])
    
    # Slide 3: Traditional LLM vs RAG
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = RGBColor(242, 242, 242)
    
    # Title
    title_shape = slide.shapes.add_shape(1, Inches(0), Inches(0), Inches(10), Inches(0.8))
    title_shape.fill.solid()
    title_shape.fill.fore_color.rgb = DARK_BLUE
    title_shape.line.color.rgb = DARK_BLUE
    title_frame = title_shape.text_frame
    p = title_frame.paragraphs[0]
    p.text = "Traditional LLM vs RAG"
    p.font.size = Pt(40)
    p.font.bold = True
    p.font.color.rgb = RGBColor(255, 255, 255)
    
    # Left column: Traditional
    left_box = slide.shapes.add_textbox(Inches(0.5), Inches(1.2), Inches(4.2), Inches(5.8))
    left_frame = left_box.text_frame
    left_frame.word_wrap = True
    
    p = left_frame.paragraphs[0]
    p.text = "❌ Traditional LLM"
    p.font.size = Pt(22)
    p.font.bold = True
    p.font.color.rgb = ACCENT
    
    traditional_points = [
        "User query → LLM",
        "Uses only training data",
        "Can hallucinate answers",
        "No context about your code",
        "Slow updates"
    ]
    
    for point in traditional_points:
        p = left_frame.add_paragraph()
        p.text = point
        p.font.size = Pt(18)
        p.level = 0
        p.space_before = Pt(6)
    
    # Right column: RAG
    right_box = slide.shapes.add_textbox(Inches(5.3), Inches(1.2), Inches(4.2), Inches(5.8))
    right_frame = right_box.text_frame
    right_frame.word_wrap = True
    
    p = right_frame.paragraphs[0]
    p.text = "✅ RAG"
    p.font.size = Pt(22)
    p.font.bold = True
    p.font.color.rgb = RGBColor(0, 176, 80)
    
    rag_points = [
        "User query → Search → Retrieve",
        "Uses YOUR code + training data",
        "Grounded in actual context",
        "Knows your architecture",
        "Real-time updates"
    ]
    
    for point in rag_points:
        p = right_frame.add_paragraph()
        p.text = point
        p.font.size = Pt(18)
        p.level = 0
        p.space_before = Pt(6)
    
    # Slide 4: RAG Pipeline Steps
    add_content_slide("RAG Pipeline: 5 Steps", [
        "1️⃣  Ingest: Load your codebase/documents",
        "2️⃣  Chunk: Split into meaningful pieces (functions, classes)",
        "3️⃣  Index: Build searchable database of chunks",
        "4️⃣  Retrieve: Find relevant chunks for the query",
        "5️⃣  Generate: Send chunks + query to LLM for answer"
    ])
    
    # Slide 5: Retrieval Strategies
    add_content_slide("Retrieval Strategies", [
        "🔑 Keyword Retrieval: Match exact keywords in text",
        "   → Fast but misses semantic meaning",
        "",
        "📊 TF-IDF (Statistical): Rank by word importance",
        "   → Better semantic understanding",
        "",
        "🎯 Hybrid: Combine both approaches",
        "   → Best of both worlds"
    ])
    
    # Slide 6: Real-World Use Cases
    add_content_slide("Real-World RAG Use Cases", [
        "📚 Customer Support: Search docs + generate answers",
        "🏗️ Architecture Review: Analyze your codebase for issues",
        "📖 Document Q&A: Chat with company knowledge base",
        "🔍 Code Analysis: Find bugs, design patterns, refactoring opportunities",
        "🎓 Learning: Interactive tutorial generation"
    ])
    
    # Slide 7: Benefits & Tradeoffs
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = RGBColor(242, 242, 242)
    
    title_shape = slide.shapes.add_shape(1, Inches(0), Inches(0), Inches(10), Inches(0.8))
    title_shape.fill.solid()
    title_shape.fill.fore_color.rgb = DARK_BLUE
    title_shape.line.color.rgb = DARK_BLUE
    title_frame = title_shape.text_frame
    p = title_frame.paragraphs[0]
    p.text = "RAG: Benefits & Tradeoffs"
    p.font.size = Pt(40)
    p.font.bold = True
    p.font.color.rgb = RGBColor(255, 255, 255)
    
    # Benefits
    benefits_box = slide.shapes.add_textbox(Inches(0.5), Inches(1.2), Inches(4.5), Inches(5.8))
    benefits_frame = benefits_box.text_frame
    benefits_frame.word_wrap = True
    
    p = benefits_frame.paragraphs[0]
    p.text = "✅ Benefits"
    p.font.size = Pt(22)
    p.font.bold = True
    p.font.color.rgb = RGBColor(0, 176, 80)
    
    for point in ["Current data", "Reduced hallucinations", "Cost-effective", "Accurate answers", "Scalable"]:
        p = benefits_frame.add_paragraph()
        p.text = point
        p.font.size = Pt(18)
        p.space_before = Pt(8)
    
    # Tradeoffs
    tradeoff_box = slide.shapes.add_textbox(Inches(5.5), Inches(1.2), Inches(4), Inches(5.8))
    tradeoff_frame = tradeoff_box.text_frame
    tradeoff_frame.word_wrap = True
    
    p = tradeoff_frame.paragraphs[0]
    p.text = "⚖️ Tradeoffs"
    p.font.size = Pt(22)
    p.font.bold = True
    p.font.color.rgb = ACCENT
    
    for point in ["Setup complexity", "Retrieval quality matters", "Latency overhead", "Storage needed", "Maintenance"]:
        p = tradeoff_frame.add_paragraph()
        p.text = point
        p.font.size = Pt(18)
        p.space_before = Pt(8)
    
    # Slide 8: AI Code Reviewer
    add_content_slide("AI Code Reviewer Project", [
        "🎯 Uses RAG to analyze Python repositories",
        "📂 Loads repo → Chunks code into functions/classes",
        "🔍 Retrieves relevant chunks for architecture analysis",
        "💭 Uses Gemini LLM to identify design smells & risks",
        "📊 Outputs structured JSON report",
        "",
        "Demo: Analyzing frigate-dev for architecture issues"
    ])
    
    # Slide 9: Closing
    add_title_slide("Questions?", "RAG makes LLMs smarter, cheaper, and more reliable")
    
    # Save presentation
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "RAG_Explanation.pptx")
    
    prs.save(output_path)
    print(f"✅ Presentation created: {output_path}")
    return output_path

if __name__ == "__main__":
    create_rag_presentation()
