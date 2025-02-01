# knowledgebase/templatetags/kb_tags.py
import logging
import re
import uuid
from django import template
from django.utils.html import format_html
from django.template.defaultfilters import slugify
from markdown import Markdown

logger = logging.getLogger(__name__)

register = template.Library()

@register.filter
def split(value, delimiter=","):
    if not value:
        return []
    return [v.strip() for v in value.split(delimiter)]

@register.simple_tag(takes_context=True)
def render_article_content(context, page):
    """
    Process RichText content from the page's fields to extract the table of contents (TOC),
    add internal links for citations, and return a dictionary with both TOC and body content
    to the template.
    """
    html_content, toc = generate_article_html_and_toc(page.body)

    context['article_data'] = {
        'toc': toc,
        'body': format_html(html_content),
    }

    return ""

def generate_article_html_and_toc(streamfield_data):
    """
    Generates the HTML content for the article, a table of contents (TOC),
    and adds internal links for citations.
    """
    html_content = ""
    toc = []
    current_h2 = None
    current_h3 = None
    heading_ids = set()
    reference_map = {}  # Map reference numbers to their IDs

    # First, process the references to create a map of reference numbers to IDs
    for block_index, block in enumerate(streamfield_data):
        if block.block_type == "references":
            for ref_index, ref in enumerate(block.value):
                ref_num = ref.get('reference_number')
                ref_id = f"ref-{ref_num}"
                reference_map[ref_num] = ref_id

                # Assign the ID to the reference in the streamfield data for later use
                block.value[ref_index]['id'] = ref_id

    # Then, process all blocks to generate HTML content and TOC
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

        elif block.block_type == "markdown":
            # Directly use the value from MarkdownBlock
            md = Markdown(extensions=['extra', 'codehilite'])
            markdown_html = md.convert(str(block.value))
            # markdown_html = add_citation_links(markdown_html, reference_map)
            html_content += f"<div class='markdown-block'>{markdown_html}</div>"

        elif block.block_type == "rich_text":
            # Convert basic Markdown-like syntax to HTML (optional)
            rich_text_html = str(block.value)
            rich_text_html = rich_text_html.replace('\n', '<br>')  # Line breaks
            rich_text_html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', rich_text_html)  # Bold
            rich_text_html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', rich_text_html)  # Italics

            # Add internal links for citations in rich text
            # rich_text_html = add_citation_links(rich_text_html, reference_map)
            html_content += f"<div class='rich-text'>{rich_text_html}</div>"

        elif block.block_type == "bullet_points":
            html_content += "<ul class='bullet-points'>"
            for item in block.value:
                html_content += f"<li>{item}</li>"
            html_content += "</ul>"
            # html_content = add_citation_links(html_content, reference_map)
        elif block.block_type == "key_facts":
            html_content += "<ul class='key-facts'>"
            for fact in block.value['content']:
                # Replace '\n' with '<br>' to create line breaks
                formatted_fact = fact.replace('\n', '<br>')
                html_content += f"<li>{formatted_fact}</li>"
            html_content += "</ul>"
        elif block.block_type == "faqs":
            html_content += "<div class='faqs'>"
            for faq in block.value:
                html_content += f"<p><strong>{faq['question']}</strong></p><p>{faq['answer']}</p>"
            html_content += "</div>"
        elif block.block_type == "references":
            html_content += "<div class='references'><ul>"
            for ref in block.value:
                ref_id = ref.get('id')  # Use the previously assigned ID
                reference_number = ref.get('reference_number', '')
                title = ref.get('title', '')
                year = ref.get('year', '')
                journal_source = ref.get('journal_source', '')
                url = ref.get('url_doi', '').strip()

                # Initialize variables for URL and link rendering
                valid_url = ""
                link_html = ""

                if url:
                    if url.startswith("http://") or url.startswith("https://"):
                        valid_url = url
                    elif url.startswith("www"):
                        valid_url = f"https://{url}"
                    elif url.startswith("10."):
                        valid_url = f"https://doi.org/{url}"
                    else:
                        # Handle other cases or leave URL empty if invalid
                        valid_url = None

                # Conditionally render the <a> tag
                if valid_url:
                    link_html = f"<a href='{valid_url}' target='_blank'>{journal_source}</a>"
                else:
                    link_html = journal_source  # No link if URL is invalid or not provided

                html_content += (
                    f"<li id='{ref_id}' class='reference'>"
                    f"<strong>{reference_number}</strong>. {title} ({year}) - {link_html}"
                    f"</li>"
                )
            html_content += "</ul></div>"

    html_content = add_citation_links(html_content, reference_map)
    # html_content = html_content.encode('latin1').decode('unicode_escape')

    return html_content, toc


def add_citation_links(text, reference_map):
    """
    Adds internal links to citations within a text block.
    """
    # Regular expression to find citations like [1] or [1, 2]
    citation_pattern = re.compile(r'\[([\d,\s]+)\]')

    def replace_citation(match):
        citation_numbers = match.group(1).split(',')
        links = []
        for number in citation_numbers:
            number = number.strip()
            if number.isdigit():
                ref_num = int(number)
                if ref_num in reference_map:
                    ref_id = reference_map[ref_num]
                    links.append(f"<a href='#{ref_id}'>[{number}]</a>")
                else:
                    links.append(f"[{number}]")  # No link if reference not found
            else:
                links.append(f"[{number}]")  # Invalid citation format
        return ", ".join(links)

    return citation_pattern.sub(replace_citation, text)