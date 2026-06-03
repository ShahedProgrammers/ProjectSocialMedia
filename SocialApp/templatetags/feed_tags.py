from django import template

register = template.Library()


@register.inclusion_tag('home/partials/feed_post.html')
def render_feed_post(post):
    return {'post': post}

