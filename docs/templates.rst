Templates
*********

Jmbo provides a generic detail template ``templates/jmbo/modelbase_detail.html`` for subclasses. This template
has been aliased to ``object_detail.html`` to follow Django naming conventions::

        {% extends "base.html" %}
        {% load jmbo_inclusion_tags jmbo_template_tags %}

        {% block extratitle %} - {{ object.title }}{% endblock %}

        {% block extrameta %}
            {% jmbocache 1200 'object-detail' object.id object.modified %}
                <link rel="canonical" href="{{ object.get_absolute_url }}" />
                <meta name="description" content="{{ object.description|default_if_none:'' }}" />
                {% with object.tags.all as tags %}
                    {% if tags %}
                        <meta name="keywords" content="{{ tags|join:", " }}" />
                    {% endif %}
                {% endwith %}
                <meta property="og:title" content="{{ object.title }}" />
                <meta property="og:type" content="article"/>
                <meta property="og:url" content="http{% if request.is_secure %}s{%endif %}://{{ request.get_host }}{{ object.get_absolute_url }}" />
                {% if object.image %}
                    <meta property="og:image" content="http{% if request.is_secure %}s{%endif %}://{{ request.get_host }}{{ object.image_detail_url }}" />
                {% endif %}
                <meta property="og:description" content="{{ object.description|default_if_none:'' }}" />
            {% endjmbocache %}
        {% endblock %}

        {% block content %}
            <div class="object-detail {{ object.class_name.lower }}-detail">

                {% with object.as_leaf_class as object %}
                    {% object_header object %}
                    {% render_object object "detail" %}
                    {% object_footer object %}
                    {% object_comments object %}
                {% endwith %}

            </div>
        {% endblock %}

Jmbo breaks a detail template into a number of elements that are customizable per content type by creating
specially named templates:

#. Header provided by ``templates/jmbo/inclusion_tags/object_header.html``.
#. Body (the meat of the item) provided by
   ``templates/jmbo/inclusion_tags/modelbase_detail.html``. This template has been
   aliased to ``templates/jmbo/inclusion_tags/object_detail.html`` to follow
   Django naming conventions.
#. Footer provided by ``templates/jmbo/inclusion_tags/object_footer.html``.
#. Comments provided by ``templates/jmbo/inclusion_tags/object_comments.html``.

