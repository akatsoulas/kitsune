from wagtail import blocks
from wagtail.admin.panels import FieldPanel
from wagtail.contrib.routable_page.models import RoutablePageMixin
from wagtail.fields import StreamField
from wagtail.models import Page
from wagtail.snippets.blocks import SnippetChooserBlock


# Wagtail: This is a StructBlock that allows selection of a Product Snippet
class ProductSnippetBlock(blocks.StructBlock):
    """Block for product snippets"""

    product = SnippetChooserBlock(target_model="products.Product", required=True)

    class Meta:
        template = "products/blocks/product_snippet_block.html"
        icon = "placehoder"
        label = "Product Card"


class SearchBlock(blocks.StructBlock):
    """Block for the search form"""

    title = blocks.CharBlock(required=True, max_length=255)
    placeholder = blocks.CharBlock(required=True, max_length=255)

    class Meta:
        template = "products/blocks/search_block.html"
        icon = "search"
        label = "Search Form"


class CTABlock(blocks.StructBlock):
    """Block for the call to action"""

    text = blocks.CharBlock(required=True, max_length=255)
    link = blocks.URLBlock(required=True)
    type = blocks.ChoiceBlock(
        choices=[
            ("Community", "Community"),
            ("Paid", "Paid"),
            ("Other", "Other"),
        ]
    )

    class Meta:
        template = "products/blocks/cta_block.html"
        icon = "plus-inverse"
        label = "Call to Action"


class FeaturedArticlesBlock(blocks.StructBlock):
    """Block for the featured articles"""

    # Need context

    class Meta:
        template = "products/blocks/featured_articles_block.html"
        icon = "doc-full-inverse"
        label = "Featured Articles"


# Wagtail: This is the product index we want to serve
class ProductIndexPage(RoutablePageMixin, Page):
    body = StreamField(
        [
            ("search", SearchBlock()),
            ("cta", CTABlock()),
            ("featured_articles", FeaturedArticlesBlock()),
            ("product_snippet", ProductSnippetBlock()),
        ]
    )

    content_panels = Page.content_panels + [FieldPanel("body")]

    def get_template(self, request):
        return "products/main.html"

    class Meta:
        verbose_name = "Product Index"
        verbose_name_plural = "Product Indexes"


class StructuralPage(Page):
    """A page used to create a folder-like structure within a page tree,
    under/in which other pages live.
    Not directly viewable - will redirect to its parent page if called"""

    # There are minimal fields on this model - only exactly what we need
    # `title` and `slug` fields come from Page->AbstractBedrockCMSPage
    is_structural_page = True
    # TO COME: guard rails on page heirarchy
    # subpage_types = []
    settings_panels = Page.settings_panels + [
        FieldPanel("show_in_menus"),
    ]
    content_panels = [
        FieldPanel("title"),
        FieldPanel("slug"),
    ]
    # promote_panels = []

    def serve(self, request):
        pass


# class SumoBasePage(Page):
#    def serve(self, request):
#        try:
#            wagtail_serve(request, path)
#        except Http404:
#            return None
#    def route(self, request, path_components):
#        pass
