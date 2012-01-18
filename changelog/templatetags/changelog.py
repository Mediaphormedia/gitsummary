from django import template
from ..models import Comment, Ticket

register = template.Library()


class CommitCommentNode(template.Node):
    def __init__(self, commit, varname):
        self.commit = template.Variable(commit)
        self.varname = varname

    def render(self, context):
        commit = self.commit.resolve(context)
        try:
            comment = Comment.objects.get(commit_sha=commit.sha)
        except Comment.DoesNotExist:
            comment = None

        context[self.varname] = comment
        return ''


@register.tag
def comment_for_commit(parser, token):
    tag_name, commit, as_, varname = token.contents.split()
    return CommitCommentNode(commit, varname)


class CommentTicketNode(template.Node):
    def __init__(self, comment, ticket, varname):
        self.commit = template.Variable(comment)
        self.ticket = template.Variable(ticket)
        self.varname = varname

    def render(self, context):
        comment = self.commit.resolve(context)
        ticket = self.ticket.resolve(context)
        try:
            ticket = comment.get_ticket_by_unicode(ticket)
        except (Ticket.DoesNotExist, AttributeError):
                ticket = None

        context[self.varname] = ticket
        return ''


@register.tag
def ticket_for_comment(parser, token):
    tag_name, comment, ticket, as_, varname = token.contents.split()
    return CommentTicketNode(comment, ticket, varname)


@register.filter
def ticket_in_db(ticket):
    try:
        return Ticket.objects.get(source=ticket.source, number=ticket.number)
    except Ticket.DoesNotExist:
        return None

