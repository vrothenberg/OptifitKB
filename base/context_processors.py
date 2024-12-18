from wagtail.models import Page

def navigation_links(request):
    if not hasattr(request, 'site'):
        return {}  # Gracefully return an empty context if `site` is missing.

    site = request.site
    root_page = site.root_page

    # Get the first live KnowledgeBaseIndexPage or None
    kb_page = root_page.get_children().type('knowledgebase.KnowledgeBaseIndexPage').live().first()

    # Get the first live AboutPage or None
    about_page = root_page.get_children().type('about.AboutPage').live().first()

    return {
        'kb_page': kb_page,
        'about_page': about_page,
    }
