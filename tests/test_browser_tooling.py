"""Unit tests for DOM inspector and browser tooling."""

import pytest
from tools.browser.dom_inspector import DOMInspector


def test_dom_inspector_structure_metrics():
    sample_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <title>Sample Government Portal</title>
        <link rel="stylesheet" href="/css/main.css">
        <script src="/js/app.js"></script>
    </head>
    <body>
        <header>
            <nav>
                <a href="/">Home</a>
                <a href="/about">About Us</a>
                <a href="https://external.gov.in/portal">External Portal</a>
                <a href="/docs/circular.pdf">Gazette Circular (PDF)</a>
            </nav>
        </header>
        <main>
            <h1>Citizen Services</h1>
            <table>
                <tr><th>Service</th><th>Fee</th></tr>
                <tr><td>Certificate</td><td>Free</td></tr>
            </table>
            <form action="/search" method="get">
                <input type="text" name="q">
                <button type="submit">Search</button>
            </form>
            <img src="/logo.png" alt="Emblem of India">
        </main>
    </body>
    </html>
    """

    res = DOMInspector.inspect(sample_html, "https://sample.gov.in")
    assert res.dom_node_count > 15
    assert res.links_count == 4
    assert res.internal_links_count == 3  # Home, About, PDF
    assert res.external_links_count == 1  # External Portal
    assert res.pdf_links_count == 1
    assert res.tables_count == 1
    assert res.forms_count == 1
    assert res.images_count == 1
    assert res.stylesheet_tags_count == 1
    assert res.script_tags_count == 1


def test_dom_inspector_framework_detection():
    angular_html = '<div ng-version="17.2.0" class="_ngcontent-c1">Angular App</div>'
    wp_html = '<link rel="stylesheet" href="/wp-content/themes/gov/style.css">'
    drupal_html = '<script src="/sites/default/files/js/drupal.js"></script>'

    assert "angular_spa" in DOMInspector.detect_frameworks(angular_html)
    assert "wordpress" in DOMInspector.detect_frameworks(wp_html)
    assert "drupal" in DOMInspector.detect_frameworks(drupal_html)
