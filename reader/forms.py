from django import forms
from django.utils.html import format_html


class StarRatingWidget(forms.widgets.RadioSelect):
    def render(self, name, value, attrs=None, renderer=None):
        html = []
        for i in range(1, 6):  # For 5 stars
            checked = 'checked="checked"' if value == i else ''
            html.append(
                f' <div class="rating rating-md"><input type="radio" name="{name}" class="mask mask-star-2 bg-orange-400" value="{i}" id="{name}-{i}" {checked} /></div>'
            )
        return format_html(''.join(html))
