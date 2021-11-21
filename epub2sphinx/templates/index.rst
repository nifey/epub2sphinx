{{ book.title }}
{{ "=" * book.title|length }}
{% if book.author %}
Author: {{ book.author }}

==============================
{% endif %}
.. toctree::
   :maxdepth: 1
   :caption: Contents:
   :name: maintoc

{% for chapter in book.toctree -%}
{{ "   %s\n"|format(chapter) }}
{%- endfor %}
Indices
==============================

* :ref:`search`
