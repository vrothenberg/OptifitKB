# knowledgebase/templatetags/kb_tags.py
import logging
import uuid
from django import template
from django.utils.html import format_html
from django.template.defaultfilters import slugify

logger = logging.getLogger(__name__)

register = template.Library()

@register.simple_tag(takes_context=True)
def render_article_content(context, page):
    """
    Process RichText content from the page's fields to extract the table of contents (TOC)
    and return a dictionary with both TOC and body content to the template.
    """
    html_content, toc = generate_article_html_and_toc(page.body)

    context['article_data'] = {
        'toc': toc,
        'body': format_html(html_content),
    }

    return ""

def generate_article_html_and_toc(streamfield_data):
    """
    Generates the HTML content for the article and a table of contents (TOC).
    """
    html_content = ""
    toc = []
    current_h2 = None
    current_h3 = None
    heading_ids = set()  # Use a set to track generated IDs

    for block in streamfield_data:
        if block.block_type == "heading":
            # Generate a unique ID for each heading based on its text content
            heading_text = block.value['heading_text']
            heading_id = slugify(heading_text)

            # Ensure ID uniqueness
            original_id = heading_id
            counter = 1
            while heading_id in heading_ids:
                heading_id = f"{original_id}-{counter}"
                counter += 1

            heading_ids.add(heading_id)

            # Append the heading to the TOC
            level = int(block.value['level'][1])  # Extract h2, h3, h4...
            if level == 2:
                current_h2 = {'text': heading_text, 'id': heading_id, 'children': []}
                toc.append(current_h2)
                current_h3 = None
            elif level == 3 and current_h2:
                current_h3 = {'text': heading_text, 'id': heading_id, 'children': []}
                current_h2['children'].append(current_h3)
            elif level == 4 and current_h3:
                current_h3['children'].append({'text': heading_text, 'id': heading_id})
            elif level == 4 and current_h2:
                current_h2['children'].append({'text': heading_text, 'id': heading_id})

            # Add the heading to the HTML content with the generated ID
            html_content += f"<h{level} id='{heading_id}'>{heading_text}</h{level}>"

        elif block.block_type == "rich_text":
            html_content += f"<div class='rich-text'>{block.value}</div>"
        elif block.block_type == "bullet_points":
            html_content += "<ul class='bullet-points'>"
            for item in block.value:
                html_content += f"<li>{item}</li>"
            html_content += "</ul>"
        elif block.block_type == "faqs":
            html_content += "<div class='faqs'><h3>FAQs</h3>"
            for faq in block.value:
                html_content += f"<p><strong>{faq['question']}</strong></p><p>{faq['answer']}</p>"
            html_content += "</div>"
        elif block.block_type == "references":
            html_content += "<div class='references'><h3>References</h3><ul>"
            for ref in block.value:
                html_content += f"<p class='reference'><strong>{ref['reference_number']}</strong>: {ref['title']} ({ref['year']}) - <a href='{ref['url_doi']}' target='_blank'>{ref['journal_source']}</a></p>"
            html_content += "</ul></div>"

    return html_content, toc