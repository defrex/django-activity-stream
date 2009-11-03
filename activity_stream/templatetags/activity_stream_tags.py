from django.template import Library, Node, TemplateSyntaxError, TemplateDoesNotExist
from activity_stream.models import ActivityFollower, ActivityStreamItem
from django.template import Variable, resolve_variable
from django.template import loader
from django.db.models import get_model
from django import template

import datetime
from misc.templatetags import smartif_tag

register = Library()

@register.inclusion_tag("follower_list.html")
def followed_by_him(user, count):
    followed = ActivityFollower.objects.filter(from_user=user).order_by('?')[0:count]
    return {"followed": followed}

@register.inclusion_tag("following_list.html")
def following_him(user, count):
    fans = ActivityFollower.objects.filter(to_user=user).order_by('?')[0:count]
    return {"following": fans}


@register.inclusion_tag("user_activity_stream.html")
def users_activity_stream(user, count):
    activity_items = ActivityStreamItem.objects.filter(actor=user, subjects__isnull=False).order_by('-created_at')[0:count]
    return {"activity_items": activity_items}

@register.inclusion_tag("friends_activity_stream.html")
def following_activity_stream(user, count):
    following =  user.following.values_list("id", flat=True)
    following = [followed for followed in following]
    following.append(user)
    activity_items = ActivityStreamItem.objects.filter(actor__in=following, subjects__isnull=False).order_by('-created_at')[0:count]
    return {"activity_items": activity_items}


class IsFollowingNode(Node):
    def __init__(self, from_user, to_user, node_true, node_false):
        self.from_user = template.Variable(from_user)
        self.to_user = template.Variable(to_user)
        self.node_true = node_true
        self.node_false = node_false
        
    def render(self, context):
        is_following = ActivityFollower.objects.filter(to_user=self.to_user.resolve(context), from_user=self.from_user.resolve(context))[:1]
        if is_following:
            return self.node_true.render(context)
        else:
            return self.node_false.render(context)

def is_following(parser, token):
    bits = token.split_contents()[1:]
    nodelist_true = parser.parse(('else', 'endif_is_following'))
    token = parser.next_token()
    if token.contents == 'else':
        nodelist_false = parser.parse(('endif_is_following',))
        parser.delete_first_token()
    else:
        nodelist_false = None
    return IsFollowingNode(bits[0], bits[1], nodelist_true, nodelist_false)

register.tag('if_is_following', is_following)