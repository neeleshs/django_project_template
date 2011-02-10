from django.template import  Library, Node, Variable, TemplateSyntaxError
from util import absolute_url
register = Library()

class AbsoluteURLNode(Node):
    def __init__(self, url):
        self.url = Variable(url)
        self.request = Variable('request')
    
    def render(self, context):
        url=self.url.resolve(context)
        req = self.request.resolve(context)
        return absolute_url(req,url)

def absolute(parser, token):
    bits = token.contents.split()
    if len(bits) != 2:
        raise TemplateSyntaxError(_('%s tag requires exactly 1 argument') % bits[0])
    return AbsoluteURLNode(bits[1])

def format_user(usr):
    from util import formatted_name as f_n
    return f_n(usr)


register.filter('format',format_user)
register.tag('absolute', absolute)
