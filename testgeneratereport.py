import weasyprint
from weasyprint import HTML, CSS
import os

# def html_to_pdf(input_html, output_pdf):
#     # Custom CSS to fix image formatting
#     custom_css = CSS(string='''
#         @page {
#             size: Letter;
#             margin: 2cm;
#         }
        
#         /* Fix for header images */
#         .header-images img {
#             width: 45% !important;
#             height: auto !important;
#             max-width: 45% !important;
#             display: block !important;
#             float: none !important;
#             margin: 0 auto !important;
#         }
        
#         /* Fix for gallery images */
#         .overview-gallery img {
#             width: calc(33% - 0.66em) !important;
#             height: 180px !important;  /* Fixed height for consistency */
#             object-fit: cover !important;
#             display: inline-block !important;
#             page-break-inside: avoid !important;
#         }
        
#         /* Prevent image overflow */
#         img {
#             max-width: 100% !important;
#             height: auto !important;
#             page-break-inside: avoid !important;`
#         }
#     ''')
    
#     HTML(input_html, base_url=os.path.dirname(os.path.abspath(input_html))).write_pdf(
#         output_pdf,
#         stylesheets=[custom_css]
#     )


from weasyprint import HTML, CSS
import os

def html_to_pdf(html_file, output_pdf, css_file=None):
    """
    Convert HTML to PDF using WeasyPrint
    
    Args:
        html_file (str): Path to input HTML file
        output_pdf (str): Path for output PDF file
        css_file (str): Optional path to external CSS file
    """
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_pdf), exist_ok=True)
    
    # Base URL for resolving relative links
    base_url = os.path.dirname(os.path.abspath(html_file))
    
    # Additional CSS for print optimization
    print_css = CSS(string="""
        @page {
            size: Letter;
            margin: 1.5cm;
            @top-right {
                content: "25 Keswick Road";
                font-size: 10pt;
                color: #666;
            }
            @bottom-center {
                content: counter(page);
                font-size: 10pt;
            }
        }
        body {
            font-size: 12pt;
            line-height: 1.6;
        }
        img {
            max-width: 100% !important;
            height: auto !important;
        }
        .page-break {
            page-break-after: always;
        }
    """)
    
    # Convert with WeasyPrint
    html = HTML(filename=html_file, base_url=base_url)
    
    if css_file:
        stylesheets = [CSS(filename=css_file), print_css]
    else:
        stylesheets = [print_css]
    
    html.write_pdf(
        output_pdf,
        stylesheets=stylesheets,
        presentational_hints=True,  # Better CSS support
        optimize_size=('fonts', 'images'),  # Compress output
        zoom=1.0  # Prevent scaling issues
    )
    print(f"Successfully created: {output_pdf}")

# Example usage
html_to_pdf(
    html_file='./x.html',
    output_pdf='./x.pdf',
    # css_file='styles.css'  # Optional - omit if CSS is embedded
)

# i = "xnew.html"
# o = "xnew.pdf"

# html_to_pdf(i, o)


