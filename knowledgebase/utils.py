# knowledgebase/utils.py
from bs4 import BeautifulSoup
import re
import uuid
import markdown
from django.utils.html import mark_safe
from wagtail.blocks import StreamValue, StreamBlock
from knowledgebase.blocks import HeadingBlock, RichTextBlock, FAQListBlock, ReferenceListBlock, BulletPointBlock
from knowledgebase.models import ArticlePage

# Define the StreamBlock used in your `ArticlePage` model
article_stream_block = StreamBlock([
    ('heading', HeadingBlock()),
    ('rich_text', RichTextBlock()),
    ('faqs', FAQListBlock()),
    ('references', ReferenceListBlock()),
    ('bullet_points', BulletPointBlock())
])


def generate_toc(html_content):
    """
    Generates a table of contents (TOC) from HTML content.
    Extracts headings (h2, h3, h4) and creates a nested structure.
    """
    try:
        soup = BeautifulSoup(html_content, 'html5lib')
    except ImportError:
        soup = BeautifulSoup(html_content, 'html.parser')

    headings = soup.find_all(['h2', 'h3', 'h4'])

    toc = []
    current_h2 = None
    current_h3 = None

    for heading in headings:
        # Generate ID for anchor link
        h_id = re.sub(r'\W+', '-', heading.text).strip('-').lower()
        h_id = f"{h_id}-{uuid.uuid4().hex[:4]}"  # Add random part to ensure uniqueness

        level = int(heading.name[1])

        if level == 2:
            current_h2 = {'text': heading.text, 'id': h_id, 'children': []}
            toc.append(current_h2)
            current_h3 = None
        elif level == 3 and current_h2:
            current_h3 = {'text': heading.text, 'id': h_id, 'children': []}
            current_h2['children'].append(current_h3)
        elif level == 4 and current_h3:
            current_h3['children'].append({'text': heading.text, 'id': h_id})
        elif level == 4 and current_h2:
            current_h2['children'].append({'text': heading.text, 'id': h_id})

    return toc


def sanitize_html(html_content):
    """
    Optionally sanitize HTML to remove unwanted tags or attributes.
    This can be useful to ensure the HTML complies with Wagtail's RichText format
    and to prevent potential XSS or formatting issues.
    """
    allowed_tags = {'h2', 'h3', 'h4', 'p', 'ul', 'ol', 'li', 'strong', 'em', 'a'}
    soup = BeautifulSoup(html_content, 'html.parser')

    # Remove disallowed tags
    for tag in soup.find_all():
        if tag.name not in allowed_tags:
          tag.decompose()

    return str(soup)


def generate_wagtail_streamfield_data(article_data):
    streamfield_data = []
    # print("generate_wagtail_streamfield_data")

    # Define the keys that we don't want to process as sections
    ignored_keys = {"title", "subtitle", "keywords", "article_image"}

    def convert_to_markdown(content):
        """Convert content to Markdown block."""
        # print("convert_to_markdown")
        return {
            "type": "markdown",
            "value": content if isinstance(content, str) else str(content)
        }


    def convert_to_bullet_points(content_list):
        """Convert a list of strings/dicts to bullet points (key_facts)."""
        # print("convert_to_bullet_points")

        # If all items are strings
        if all(isinstance(item, str) for item in content_list):
            bullet_points_list = [item for item in content_list]
            # print(bullet_points_list)

            return {
                "type": "bullet_points",
                "value": bullet_points_list
            }

        elif all(isinstance(item, dict) and len(item) == 1 for item in content_list):
            # All items are dictionaries with a single key
            return {
                "type": "bullet_points",
                "value": [{"content": list(item.values())[0]} for item in content_list]
            }
        elif all(isinstance(item, dict) and len(item) > 1 for item in content_list):
            # Two-key dictionaries
            return {
                "type": "bullet_points",
                "value": [
                    {
                        "content": "\n".join(
                            f"{key.capitalize()}: {value}" for key, value in item.items()
                        )
                    }
                    for item in content_list
                ]
            }

        # Mixed types or unknown structure, fallback
        return {
            "type": "rich_text",
            "value": "\n".join(str(item) for item in content_list)
        }

    def convert_to_rich_text(content_str):
        """Convert a string (markdown) to rich text."""
        # print("convert_to_rich_text")
        html_content = markdown.markdown(content_str)
        return {
            "type": "rich_text",
            "value": html_content
        }

    for key, section in article_data.items():
        if key in ignored_keys:
            continue
        if not (isinstance(section, dict) and "heading" in section and "content" in section):
            continue

        heading = section.get("heading", "")
        content = section.get("content", "")

        # print("SECTION:", heading)

        # Add the heading
        if heading:
            streamfield_data.append({
                "type": "heading",
                "value": {
                    "heading_text": heading,
                    "level": "h2"
                }
            })

        # Handle each section by heading
        if heading == "Key Facts":
            # Usually bullet points (list). If dict-based, handle accordingly.
            if isinstance(content, list):
                streamfield_data.append(convert_to_bullet_points(content))
            elif isinstance(content, str):
                streamfield_data.append(convert_to_markdown(content))

        elif heading == "Symptoms":
            # Similar to key facts, often bullet points
            if isinstance(content, list):
                streamfield_data.append(convert_to_bullet_points(content))
            elif isinstance(content, str):
                streamfield_data.append(convert_to_markdown(content))

        elif heading == "Types":
            # Could be markdown with ### subheadings or bullet points
            if isinstance(content, str):
                streamfield_data.append(convert_to_markdown(content))
            else:
                # If unexpected format, fallback
                if isinstance(content, list):
                    streamfield_data.append(convert_to_bullet_points(content))

        elif heading == "Causes":
            # Likely a string, convert to rich_text
            if isinstance(content, str):
                streamfield_data.append(convert_to_markdown(content))
            else:
                # If it's a list, treat as bullet points
                if isinstance(content, list):
                    streamfield_data.append(convert_to_bullet_points(content))

        elif heading == "Risk Factors":
            # Usually bullet points
            if isinstance(content, list):
                streamfield_data.append(convert_to_bullet_points(content))
            elif isinstance(content, str):
                streamfield_data.append(convert_to_markdown(content))

        elif heading == "Diagnosis":
            # Often markdown subheadings
            if isinstance(content, str):
                streamfield_data.append(convert_to_markdown(content))
            else:
                # If list, handle as bullet points
                if isinstance(content, list):
                    streamfield_data.append(convert_to_bullet_points(content))

        elif heading == "Prevention":
            # Usually bullet points
            if isinstance(content, list):
                streamfield_data.append(convert_to_bullet_points(content))
            elif isinstance(content, str):
                streamfield_data.append(convert_to_markdown(content))

        elif heading == "Lifestyle":
            if isinstance(content, str):
               streamfield_data.append(convert_to_markdown(content))
            elif isinstance(content, list):
                streamfield_data.append(convert_to_bullet_points(content))
            else:
                streamfield_data.append({
                     "type": "rich_text",
                     "value": str(content)
                 })

        elif heading == "Specialist to Visit":
            # Probably a string
            if isinstance(content, str):
                streamfield_data.append(convert_to_markdown(content))
            else:
                streamfield_data.append(convert_to_bullet_points(content) if isinstance(content, list) else {
                    "type": "rich_text",
                    "value": str(content)
                })

        elif heading == "Treatment":
            # Likely a string
            if isinstance(content, str):
                streamfield_data.append(convert_to_markdown(content))
            else:
                streamfield_data.append(convert_to_bullet_points(content) if isinstance(content, list) else {
                    "type": "rich_text",
                    "value": str(content)
                })

        
        elif heading == "Home-Care":
            # Usually bullet points
            if isinstance(content, list):
                streamfield_data.append(convert_to_bullet_points(content))
            elif isinstance(content, str):
                streamfield_data.append(convert_to_markdown(content))

        elif heading == "Living With":
            # Usually text
            if isinstance(content, str):
                streamfield_data.append(convert_to_markdown(content))
            else:
                streamfield_data.append(convert_to_bullet_points(content))

        elif heading == "Complications":
            # Usually text
            if isinstance(content, str):
                streamfield_data.append(convert_to_markdown(content))
            else:
                streamfield_data.append(convert_to_bullet_points(content))

        elif heading == "Alternative Therapies":
            # Usually text
            if isinstance(content, str):
                streamfield_data.append(convert_to_markdown(content))
            else:
                streamfield_data.append(convert_to_bullet_points(content))

        

        elif heading == "FAQs":
            # Expect a list of dict with question/answer
            if isinstance(content, list) and all(isinstance(item, dict) and "question" in item and "answer" in item for item in content):
                streamfield_data.append({
                    "type": "faqs",
                    "value": [{"question": item["question"], "answer": item["answer"]} for item in content]
                })
            else:
                # Fallback to bullet points or rich text
                if isinstance(content, list):
                    streamfield_data.append(convert_to_bullet_points(content))
                elif isinstance(content, str):
                    streamfield_data.append(convert_to_markdown(content))

        elif heading == "References":
            # Expect a list of dict with reference info
            if isinstance(content, list):
                references = []
                for ref in content:
                    try:
                        # Validate and sanitize each reference
                        reference_number = ref.get("reference_number", None)
                        authors = ref.get("authors", "")
                        year = ref.get("year", "")
                        title = ref.get("title", "")
                        journal_source = ref.get("journal_source", "")
                        url_doi = ref.get("url_doi", "")

                        # Ensure critical fields are present
                        if not reference_number or not title:
                            print(f"Skipping invalid reference: {ref}")
                            continue  # Skip invalid references

                        # Append cleaned reference
                        references.append({
                            "reference_number": reference_number,
                            "authors": authors or "Unknown",
                            "year": year or "Unknown",
                            "title": title,
                            "journal_source": journal_source or "N/A",
                            "url_doi": url_doi or ""
                        })
                    except Exception as e:
                        print(f"Error processing reference {ref}: {e}")
                        continue
                        # Add the references to the StreamField data

                if references:
                    # print("if references")
                    # print(references)
                    streamfield_data.append({
                        "type": "references",
                        "value": references
                    })
                else:
                    print("No valid references found in the section.")
            else:
                # Fallback
                if isinstance(content, list):
                    streamfield_data.append(convert_to_bullet_points(content))
                elif isinstance(content, str):
                    streamfield_data.append(convert_to_markdown(content))

        else:
            # For headings not specifically handled above or if heading is empty:
            if isinstance(content, list):
                streamfield_data.append(convert_to_bullet_points(content))
            elif isinstance(content, str):
                streamfield_data.append(convert_to_markdown(content))
            elif isinstance(content, dict):
                # Unknown dict structure
                streamfield_data.append({
                    "type": "rich_text",
                    "value": "\n".join(f"{key}: {value}" for key, value in content.items())
                })
            else:
                # Fallback
                streamfield_data.append({
                    "type": "rich_text",
                    "value": str(content)
                })

    body_field = ArticlePage._meta.get_field("body")
    block_def = body_field.stream_block
    

    return streamfield_data