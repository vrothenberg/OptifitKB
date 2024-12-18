from wagtail.models import Page
from django.conf import settings
from django.utils.http import url_has_allowed_host_and_scheme

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


# def breadcrumbs(request):
#     breadcrumbs = []
#     if hasattr(request, 'path'):
#         path = request.path
#         if path != '/':
#             # Check for path prefix and remove it if it exists
#             if settings.SITE_PREFIX:  # Assuming your setting is called SITE_PREFIX
#                 path = path.replace(settings.SITE_PREFIX, '', 1)
#             path = path.rstrip('/')
#             print(f"Trying path (normalized): '{path}'")
#             try:
#                 page = Page.objects.get(url_path=path)
#                 print(f"Found page: {page.title} (url_path: {page.url_path})")
#                 ancestors = page.get_ancestors(inclusive=True).exclude(pk=page.get_root().pk)
#                 breadcrumbs = list(ancestors)
#                 for crumb in breadcrumbs:
#                     print(f"Ancestor: {crumb.title} (url_path: {crumb.url_path})")
#             except Page.DoesNotExist:
#                 print(f"Page does not exist for path: '{path}'")
#             except Exception as e:
#                 print(f"An error occurred: {e}")

#     print(f"Final breadcrumbs: {breadcrumbs}")
#     return {'breadcrumbs': breadcrumbs}