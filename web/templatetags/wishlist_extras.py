from django import template

register = template.Library()


@register.tag
def percentage(parser, token):
    try:
        # split_contents() knows not to split quoted strings.
        tag_name, part, total = token.split_contents()
    except ValueError:
        t = token.contents.split()[0]
        raise template.TemplateSyntaxError(
            "%r tag requires exactly two arguments" % t)

    return PercentageNode(part, total)


class PercentageNode(template.Node):
    def __init__(self, part, total):
        self.part = template.Variable(part)
        self.total = template.Variable(total)

    def render(self, context):
        try:
            part_value = float(self.part.resolve(context))
            total_value = float(self.total.resolve(context))
        except ValueError:
            raise template.TemplateSyntaxError(
                "percentage tag arguments should be numbers")

        if total_value == 0:
            raise template.TemplateSyntaxError(
                "percentage tag's second argument can not be 0")

        return str(part_value * 100 / total_value) + '%'
