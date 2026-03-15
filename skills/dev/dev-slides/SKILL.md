---
name: dev-slides
description: Generate a Google Slides presentation from a paper PDF URL using gws CLI.
---

# Paper-to-Slides Generator

## Usage
```
/dev-slides <arxiv PDF URL or paper URL>
```

## Prerequisites
- `gws` CLI authenticated with Slides and Drive APIs
- Python packages: `pymupdf`, `Pillow`, `numpy`

## Presentation Style
- Title slide: 個人進度報告 / 電機所碩一 邱冠銘
- Section headers: TITLE layout (CENTERED_TITLE), left-aligned
- Content slides: TITLE_AND_BODY layout (single column, not two columns)
- Fonts: theme defaults (no overrides)
- Body: bullet points with lineSpacing 150, indent 36pt (level 0), 72pt (level 1)
- Sub-items use level 1 indentation for hierarchy
- Keep each slide concise, 3-5 bullet points max per slide

## Slide Structure
1. Title slide (TITLE layout): 個人進度報告 + 電機所碩一 邱冠銘
2. Paper info slide (TITLE_AND_BODY): paper title as slide title, body lists authors, affiliation, conference/year, arXiv ID
3. Section: Intro
4. Motivation & Problem (content slide)
5. Paper Goal (content slide)
6. Section: Design
7. Method slides (2-4 slides depending on paper complexity)
8. Figure slides (from paper, with captions)
9. Section: Eval
10. Experimental setup (content slide)
11. Results (content slide)
12. Table/figure slides (from paper, with captions)
13. Section: Conclusion
14. Limitations & Key Takeaways (content slide)
15. Thanks slide

## Instructions

1. **Fetch paper content:**
   - Use `WebFetch` on the arxiv abstract page to get title, authors, abstract
   - Use `WebFetch` on the PDF URL for detailed methodology, results, contributions

2. **Create presentation:**
   ```
   gws slides presentations create --json '{"title": "<paper title>"}'
   ```
   Save the `presentationId` from the response.

3. **Get layout IDs** from the create response:
   - TITLE layout (for section headers + title slide)
   - TITLE_AND_BODY layout (for content slides)
   - TITLE_ONLY layout (for figure/table slides)

4. **Build slides via batchUpdate:**
   - Delete the default empty slide first
   - Create ALL slides listed in the Slide Structure section, do not skip any (especially the paper info slide)
   - Create all slides with `createSlide`, mapping placeholders by type
   - Object IDs must be at least 5 characters
   - Insert text with `insertText`
   - Apply bullets with `createParagraphBullets` (preset: `BULLET_DISC_CIRCLE_SQUARE`)
   - Set paragraph styles: lineSpacing 150, indent 36pt/72pt for level 0/1
   - Alignment enum: use `START` not `LEFT`, use `CENTER` not `CENTER`
   - Send all requests in a single `batchUpdate` call

5. **Extract figures from PDF:**
   - Download PDF: `curl -sL "<url>" -o /tmp/paper.pdf`
   - Use `pymupdf` to analyze exact figure boundaries: call `page.get_text("dict")` for text blocks and `page.get_drawings()` for drawing bounds
   - Define precise `fitz.Rect` clip regions based on analyzed coordinates, not rough guesses
   - Auto-crop remaining whitespace with PIL + numpy (threshold gray < 248)
   - Target key figures: overview diagram, method diagram, result tables

6. **Upload images** to a public host:
   ```bash
   curl -s -X POST "https://freeimage.host/api/1/upload" \
     -F "key=6d207e02198a847aa98d0a2a901485a5" \
     -F "source=@/tmp/paper_figs/fig.png" \
     -F "format=json"
   ```
   Extract URL from response: `.image.url`

7. **Insert images into slides** via batchUpdate:
   - Use TITLE_ONLY layout for figure slides
   - `createImage` with the hosted URL
   - Position: centered horizontally, image top at ~1250000 EMU (0.25" below title bottom)
   - Add caption text box below image: 12pt, gray (#666), centered
   - Caption top = image bottom + 150000 EMU gap
   - Scale images to fit: max image bottom at ~4400000 EMU, keep aspect ratio

8. **Verify layout** after building all slides:
   - Programmatically check every slide for overflow: compute each element's bounding box (size * scale + translate) and verify it stays within slide bounds (9144000 x 5143500 EMU)
   - Verify title-to-image gap >= 228600 EMU (0.25")
   - Verify image-to-caption gap ~150000 EMU, consistent across slides
   - Verify caption bottom < 5000000 EMU
   - Fix any violations in a single batchUpdate pass

9. **Output** the presentation URL:
   ```
   https://docs.google.com/presentation/d/<presentationId>/edit
   ```

## Rules
- If a slide title wraps to multiple lines, move the body placeholder down using `updatePageElementTransform` to avoid overlap (increase translateY)
- Always use `batchUpdate` for efficiency, combine as many requests as possible
- Keep bullet text short, one line per point
- Use level 1 bullets for sub-items, not "- " prefixes
- Crop figures tightly, no excess whitespace
- Caption each figure/table with a one-line description
- Do not override theme fonts or colors
- Never let images overlap or sit too close to the title (min 0.25" gap)
- Position captions relative to actual image bottom, not at fixed absolute Y
- Always run a post-creation overflow check on all slides before finishing
