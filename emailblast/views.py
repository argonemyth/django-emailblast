# coding=utf-8
from django.conf import settings
from django.http import HttpResponse
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.sites.models import RequestSite
from django.contrib.auth.decorators import permission_required
from django.views.generic.simple import redirect_to
from django.template import RequestContext, Context, loader
from django.shortcuts import render_to_response, get_object_or_404
from django.utils.translation import ugettext_lazy as _

from emailblast.models import Newsletter, Subscription, Email, SentLog
from emailblast.tasks import render_email


#@permission_required('emailblast.change_newsletterissue')
def email_preview(request, id, format="html"):
    """
    Render the specified newsletter email with a random EmailAddress
    so an admin can preview a newsletter before mailing it.
    """
    email = get_object_or_404(Email, pk=id)
    html_template, text_template = email.newsletter.get_templates()
    subscribers = email.newsletter.subscription.select_related()

    if subscribers.count() > 0:
        recipient = subscribers[0]

    # Construct the email
    email_context = Context({ 'email': email,
                            'recipient': recipient.name })
    text_content, html_content = render_email(email_context,
                                              text_template,
                                              html_template)
    if format == "html":
        return HttpResponse(html_content)
    else:
        return HttpResponse(text_content, mimetype='text/plain')


def view_email(request, slug):
    """
    Render the specified newsletter email for users who can't view
    HTML emails on their mail clients.
    """
    email = get_object_or_404(Email, slug=slug)
    html_template, text_template = email.newsletter.get_templates()
    recipient = request.user.profile.get_full_name_or_username()

    # Construct the email
    email_context = Context({ 'email': email,
                            'recipient': recipient })
    text_content, html_content = render_email(email_context,
                                              text_template,
                                              html_template)
    return HttpResponse(html_content)
