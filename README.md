# OptiFit Knowledge Base

This project is a knowledge base application built using Wagtail, a Django-based Content Management System (CMS). It's designed to provide a structured, searchable, and easily navigable repository of information, particularly focused on health and wellness topics.

## Project Overview

The knowledge base is organized into a hierarchy of:

*   **Index Page:** The top-level entry point that lists all available categories.
*   **Category Pages:** Group related articles under a common theme (e.g., "Bites", "Brain Health").
*   **Article Pages:** The core content units, containing detailed information on specific topics.

## Key Features and Functionality

1. **Structured Content:**
    *   Article content is managed using Wagtail's `StreamField`, allowing editors to create rich content using a variety of blocks.
    *   Custom blocks like `HeadingBlock`, `RichTextBlock`, `KeyFactsBlock`, `FAQListBlock`, `ReferenceListBlock`, `BulletPointBlock`, and `MarkdownBlock` enable structured and formatted content.
    *   The `KeyFactsBlock` allows for a list of key points, useful for summarizing important information.
    *   The `FAQListBlock` provides a way to present frequently asked questions and their answers.
    *   The `ReferenceListBlock` allows for formatted citations with links to external sources, automatically generating anchor links for internal citations.
    *   The `MarkdownBlock` supports markdown input, including extensions for extra features and code highlighting.

2. **Automated Table of Contents (TOC):**
    *   Each `ArticlePage` automatically generates a nested table of contents based on the `h2`, `h3`, and `h4` headings within the content.
    *   The TOC is displayed in a sticky sidebar for easy navigation.
    *   Unique IDs are generated for each heading to ensure correct internal linking.
    *   Smooth scrolling to sections when clicking on TOC links is implemented.

3. **Citation and Reference Handling:**
    *   The `ReferenceListBlock` allows editors to add structured references with fields for reference number, authors, year, title, journal/source, and URL/DOI.
    *   The `kb_tags` templatetag includes logic to parse the content and automatically create internal links from citations (e.g., `[1]`) to their corresponding entries in the reference list.

4. **Import/Export Functionality:**
    *   Management commands are provided to import articles from JSON files (`import_articles.py`) and to delete existing articles (`delete_all_articles.py`, `delete_empty_categories.py`).
    *   The import process handles creating or updating `ArticlePage` instances and correctly maps the structured JSON data to Wagtail's `StreamField` blocks.

5. **Custom Context Processors:**
    *   The `navigation_links` context processor makes `kb_page` (Knowledge Base Index) and `about_page` available to all templates for easy navigation.

6. **Site Settings:**
    *   The `SiteSettings` model (registered as a Wagtail setting) allows administrators to configure the site name and footer text through the Wagtail admin.
    *   The `NavigationSettings` model allows managing social media links (LinkedIn, GitHub, Mastodon).

7. **Templating:**
    *   The project uses standard Wagtail templating practices with base templates (`base.html`) and includes for reusable components (e.g., `navigation.html`, `sidebar_toc.html`, `breadcrumb.html`).
    *   Custom template tags are used for rendering the table of contents (`render_article_content`) and handling footer text (`get_footer_text`).

## Getting Started

1. **Installation:**
    *   Set up a Python virtual environment.
    *   Install the required packages: `pip install -r requirements.txt` (you'll need to create a `requirements.txt` based on the provided code).
    *   Configure your database settings in `optifit_kb/settings/dev.py` (or `production.py` for production).

2. **Database Migrations:**
    *   Run database migrations: `python manage.py migrate`

3. **Create Superuser:**
    *   Create a superuser to access the Wagtail admin: `python manage.py createsuperuser`

4. **Run Development Server:**
    *   Start the development server: `python manage.py runserver`

5. **Access Wagtail Admin:**
    *   Go to `http://127.0.0.1:8000/admin` and log in with your superuser credentials.

6. **Initial Setup:**
    *   Create a `HomePage` (under the automatically created `Root` page).
    *   Create an `IndexPage` under the `HomePage`.
    *   Create at least one `CategoryPage` under the `IndexPage`.
    *   Go to `Settings` > `Sites` in the Wagtail admin and set the `HomePage` as the default site.

## Importing Articles (Optional)

1. **Prepare your JSON data:**
    *   The JSON file should be structured according to the format expected by the `import_articles` command (you can infer the structure from the `generate_wagtail_streamfield_data` function in `utils.py`).

2. **Run the import command:**

    ```bash
    python manage.py import_articles --category-name "Your Category Name" --json-path path/to/your/file.json
    ```

    Replace `"Your Category Name"` with the name of the category you want to import articles into, and `path/to/your/file.json` with the path to your JSON file.

## Development Notes

*   The project structure follows standard Wagtail/Django conventions.
*   Static files (CSS, JavaScript, images) are located in the `static` directory.
*   Templates are located in the `templates` directory, organized by app.
*   The `project_explorer.py` script is a utility to generate a text file describing the project structure and content (used to provide context for this README).
*   The Javascript file `toc-highlight.js` highlights the current section in the sidebar.

## Further Improvements

*   The commented-out `breadcrumbs` context processor could be completed and integrated into the templates.
*   Consider adding more comprehensive unit tests.
*   The project could benefit from more detailed documentation, especially regarding the JSON import format and the custom `StreamField` blocks.
