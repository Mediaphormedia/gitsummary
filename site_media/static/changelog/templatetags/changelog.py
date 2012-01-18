from django import template
from ..models import Comment

register = template.Library()


class CommitCommentNode(template.Node):
    def __init__(self, commit, varname):
        self.commit = template.Variable(commit)
        self.varname = varname

    def render(self, context):
        commit = self.commit.resolve(context)
        try:
            comment = Comment.objects.get(commit_sha=commit['hexsha'])
        except Comment.DoesNotExist:
            comment = None

        context[self.varname] = comment
        return ''


@register.tag
def comment_for_commit(parser, token):
    tag_name, commit, as_, varname = token.contents.split()
    return CommitCommentNode(commit, varname)
