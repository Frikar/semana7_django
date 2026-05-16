from django.test import SimpleTestCase

from .templatetags.chat_markdown import markdown_content


class MarkdownContentFilterTests(SimpleTestCase):
    def test_renders_common_markdown(self):
        content = """# Titulo

Texto con **negrita**, *cursiva* y `codigo`.

- Uno
- Dos

```python
print("hola")
```"""

        rendered = markdown_content(content)

        self.assertIn('<h1>Titulo</h1>', rendered)
        self.assertIn('<strong>negrita</strong>', rendered)
        self.assertIn('<em>cursiva</em>', rendered)
        self.assertIn('<code>codigo</code>', rendered)
        self.assertIn('<ul><li>Uno</li><li>Dos</li></ul>', rendered)
        self.assertIn('<pre><code class="language-python">print(&quot;hola&quot;)</code></pre>', rendered)

    def test_escapes_raw_html(self):
        rendered = markdown_content('<script>alert("x")</script>')

        self.assertNotIn('<script>', rendered)
        self.assertIn('&lt;script&gt;', rendered)
