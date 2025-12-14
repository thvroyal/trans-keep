# 4. Data Processing Pipeline

## 4.1 PDF Extraction (PDFMathTranslate)

**Technology:** PDFMathTranslate (pdf2zh) with DocLayout-YOLO for AI-powered layout detection

**Algorithm:**
```python
def extract_text_with_layout(pdf_path):
    # Uses PDFMathTranslate (pdf2zh) with DocLayout-YOLO
    # for better format preservation of technical documents
    
    from pdf2zh_next.babeldoc import BabelDoc
    from pdf2zh_next.settings import SettingsModel
    
    settings = SettingsModel()
    babel_doc = BabelDoc(pdf_path, settings)
    babel_doc.parse()
    
    results = []
    for page_idx, page in enumerate(babel_doc.pages):
        for block in page.blocks:
            results.append({
                "page": page_idx,
                "text": block.text,
                "bbox": block.bbox,  # Coordinates for reconstruction
                "font_size": block.font_size,
                "font_name": block.font_name,
                "is_bold": block.is_bold,
                "is_italic": block.is_italic,
                "rotation": block.rotation
            })
    
    return results
```

**Advantages:**
- AI-powered layout detection (DocLayout-YOLO)
- Specialized for scientific/technical documents
- Better preservation of tables, equations, multi-column layouts
- Open source with active development

**Performance:**
- Performance characteristics to be determined through testing
- May have different performance profile than PyMuPDF
- Expected: Similar or better for complex layouts
- 500-page document: Performance testing required

## 4.2 Translation Pipeline (Batching)

**Strategy:**
- Group extracted text blocks by page
- Batch translate 10 blocks at once (DeepL API efficiency)
- Parallelize across pages using Celery

```python
async def translate_blocks(blocks, target_language):
    for page_blocks in batch_by_page(blocks):
        futures = []
        for block_batch in batch(page_blocks, size=10):
            texts = [b["text"] for b in block_batch]
            future = await deepl.translate_async(
                texts,
                target_lang=target_language
            )
            futures.append(future)
        
        # Await all futures for this page
        results = await asyncio.gather(*futures)
```

**Cost & Time:**
- DeepL: ~$0.15 per 100k words
- 100-page document (50k words): ~$0.075
- Processing time: 30-60 seconds

## 4.3 Tone Customization (Claude Haiku)

**When Applied:**
- Initial translation complete → Default tone (neutral)
- User clicks tone preset → Re-apply with tone
- Uses Claude 3.5 Haiku (lightweight, fast)

**Example Prompt:**
```
Current translation: "The system works well."
Target tone: Creative
Target context: Novel translation

Rewrite this translation in the target tone, preserving all meaning:
"The system works well."

Return ONLY the rewritten text.
```

**Response:**
```
The system hums with graceful efficiency.
```

**Cost & Time:**
- Claude Haiku: ~$0.80 per 1M input tokens
- 100 pages (~60k tokens): ~$0.048
- Processing: 15-30 seconds

## 4.4 PDF Reconstruction & Editing Flow

**Technology:** PDFMathTranslate (pdf2zh) for reconstruction with better format preservation

**Reconstruction Algorithm:**
- Uses PDFMathTranslate's reconstruction capabilities
- Better preservation of complex layouts (tables, equations, multi-column)
- Maintains fonts, sizes, styles, and page layout
- Handles technical documents with superior format preservation

**Critical Decision: How to Handle User Edits**

When user edits a block AFTER translation, we have three options:

### **Option A: In-Memory Edit Tracking (RECOMMENDED for MVP)**

**How it works:**
```python
# Frontend maintains edit state in Zustand store
edits = {
  "block_id_1": "User's edited translation",
  "block_id_5": "Another edit",
}

# When downloading, apply edits before generating PDF
def generate_download_pdf(original_blocks, translated_blocks, edits):
    final_blocks = translated_blocks.copy()
    
    for block_id, edited_text in edits.items():
        final_blocks[block_id]["text"] = edited_text
    
    return reconstruct_pdf_from_blocks(original_blocks, final_blocks)
```

**Performance:**
- ✅ Fast (edits stored in memory, no DB writes)
- ✅ Simple (no complex PDF manipulation)
- ✅ No rebuild until download
- ❌ Edits lost if user closes browser (acceptable for MVP)

**Cost:** $0 additional overhead

---

### **Option B: Rebuild Just-Modified Block**

**How it works:**
```python
# When user edits a block, rebuild ONLY that block
# Uses PDFMathTranslate for better format preservation
def update_pdf_block(pdf_path, block_id, new_text):
    from pdf2zh_next.babeldoc import BabelDoc
    from pdf2zh_next.settings import SettingsModel
    
    settings = SettingsModel()
    babel_doc = BabelDoc(pdf_path, settings)
    babel_doc.parse()
    
    # Update specific block
    page = babel_doc.pages[block_id["page"]]
    block = page.blocks[block_id["block_id"]]
    block.text = new_text
    
    # Reconstruct PDF
    babel_doc.save(output_path)
    return output_path
```

**Performance:**
- ✅ Medium complexity (one block at a time)
- ✅ Faster than full rebuild
- ✅ Changes visible immediately
- ❌ Still requires PDF manipulation (complex)

**Cost:** Minimal (just PDFBox operations)

---

### **Option C: Full PDF Rebuild**

**How it works:**
```python
# Reconstruct entire PDF from scratch whenever user edits
# Uses PDFMathTranslate for better format preservation
def full_reconstruct_pdf(original, all_translated_blocks_with_edits):
    from pdf2zh_next.babeldoc import BabelDoc
    from pdf2zh_next.settings import SettingsModel
    
    # Load original PDF
    settings = SettingsModel()
    babel_doc = BabelDoc(original, settings)
    babel_doc.parse()
    
    # Apply all translated blocks with edits
    for block_data in all_translated_blocks_with_edits:
        page = babel_doc.pages[block_data["page"]]
        block = page.blocks[block_data["block_id"]]
        block.text = block_data["translated_text"]
    
    # Reconstruct PDF
    babel_doc.save(output_path)
    return output_path
```

**Performance:**
- ❌ SLOW (rebuild entire 500-page PDF for one edit)
- ❌ High CPU cost (10-30 seconds)
- ❌ Not acceptable for user experience

---

## **RECOMMENDATION: Option A (In-Memory + Rebuild on Download)**

**Why:**
1. **MVP speed:** Get to launch fast (no complex PDF manipulation)
2. **Performance:** Instant edit feedback (no rebuild delay)
3. **Cost:** Minimal ($0 additional)
4. **Simplicity:** Just track edits in frontend state

**Implementation:**

**Frontend (React + Zustand):**
```typescript
interface EditStore {
  edits: Map<string, string>  // block_id → edited_text
  
  editBlock(blockId: string, newText: string) {
    this.edits.set(blockId, newText)
    // Show updated text immediately in ReviewPanel
  }
  
  async downloadPDF() {
    const response = await api.download(jobId, {
      edits: Array.from(this.edits.entries())  // Send edits to backend
    })
    // Download file
  }
}
```

**Backend (FastAPI):**
```python
@router.get("/api/v1/download/{job_id}")
async def download_translation(job_id: str, edits: List[Tuple[str, str]]):
    # Load original PDF and translated blocks
    original_pdf = load_original_from_s3(job_id)
    translated_blocks = load_translated_blocks_from_cache(job_id)
    
    # Apply edits
    for block_id, new_text in edits:
        translated_blocks[block_id]["translated_text"] = new_text
    
    # Reconstruct with edits using PDFMathTranslate
    final_pdf = PDFReconstructionService.reconstruct_pdf(
        original_pdf_bytes=original_pdf,
        translated_blocks=translated_blocks
    )
    
    return final_pdf
```

**Performance:**
- Edit feedback: Instant (just update Zustand state)
- Download: 5-15 seconds (rebuild with edits applied)
- User experience: Excellent (responsive editing, clean download)

---

## **Phase 2: Optimize Editing**

**If editing becomes a bottleneck:**
- Implement Option B (rebuild just-edited blocks)
- Or: Switch to HTML rendering (edit in HTML → export to PDF)
- Store edit history in database (undo/redo)

**For now:** Keep Option A, launch fast!

---
