from django.core.mail import EmailMultiAlternatives
from django.template import loader, Context, TemplateDoesNotExist
from django.template.loader import render_to_string
from celery import task
import smtplib
from time import sleep
from pynliner import Pynliner
from emailblast.models import Email, SentLog


class UnicodeSafePynliner(Pynliner):
    def _get_output(self):
        """
        Generate Unicode string of `self.soup` and set it to `self.output`

        Returns self.output
        """
        self.output = unicode(self.soup)
        return self.output


class NoContent(Exception):
    """
    Will raise when there is there is no text or html content.
    """
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


def render_email(context, text_template, html_template=None):
    """
    Render a email given by the template name
    """
    try:
        t = loader.get_template(text_template)
        text_content = t.render(context)
    except TemplateDoesNotExist:
        text_content = None

    if html_template:
        try:
            html_content = UnicodeSafePynliner().from_string(
                render_to_string(html_template, context)).run()
        except TemplateDoesNotExist:
            html_content = None
    else:
        html_content = None

    """
    if email.image:
        t = loader.get_template("emails/mailblast.html")
        c = Context({'image_url': settings.IMAGE_HOST+str(email.image.url)})
        html_content = t.render(c) 
    else:
        html_content = None
    """

    if not text_content and not html_content:
        #print "None of the following two templates are found: %s and %s" % (text_template, html_template)
        raise NoContent("None of the following two templates are found: %s and %s" % (text_template, html_template))

    return text_content, html_content


@task()
def send_newsletter(email):
    """
    The task accepts a newsletter email and send it to all the subscribers.
    It skip the subscribers we already sent the email to.
    """
    email.change_status(2)
    sender = email.newsletter.get_sender()
    html_template, text_template = email.newsletter.get_templates()
    total_subscribers = str(email.newsletter.subscription.count())
    composer = email.newsletter.get_sender()
    listname = email.newsletter.title
    #blast_logger.info('Mailblast %s to %s started, from %s, %s recipients on the list, sent as %s.' % (email.subject, listname, composer, email_count, str(email.sender)))
    #mail_admins('Blast Started', composer + " is going to send " + email_count+ " emails from " + listname + " as " + str(email.sender))
    print 'Mailblast %s to %s started, from %s, %s recipients on the list.' % (email.subject, listname, composer, total_subscribers)

    for subscription in email.newsletter.subscription.select_related():
        recipient = subscription.get_recipient()
        try:
            email.send_log.get(to__iexact=subscription.email)
        except: 
            # Construct the email
            email_context = Context({ 'email': email,
                                    'recipient': subscription.name })
            text_content, html_content = render_email(email_context,
                                                      text_template,
                                                      html_template)
            if html_content:
                msg = EmailMultiAlternatives(email.subject, text_content, 
                                             sender, [recipient])
                msg.attach_alternative(html_content, "text/html")
            else:
                msg = EmailMessage(email.subject, text_content, sender,
                                  [recipient])
            """
            if html_content:
                msg.attach_alternative(html_content, "text/html")
            elif email.file:
                msg.attach_file(email.file.path)
            """

            try:
                msg.send()
                db_log = SentLog(email=email, to=subscription.email, result=1)
                db_log.save()
                #blast_logger.info(to_email.infoValue + " - Email Sent")
                print subscription.email + " - Email Sent"
                sleep(20)
            except (smtplib.SMTPSenderRefused, smtplib.SMTPRecipientsRefused, smtplib.SMTPAuthenticationError), err:
                #EmailLog.objects.log(email, to_email.infoValue, 2, log_message=str(err))
                db_log = SentLog(email=email, to=subscription.email, result=2,
                                 log_message=str(err))
                db_log.save()
                #blast_logger.error("%s - Failer %s" % (to_email.infoValue, err))
                print "%s - Failer %s" % (subscription.email, err)
            except Exception as e:
                #EmailLog.objects.log(email, to_email.infoValue, 4, log_message=u"Unknown error %s" % (str(e)))
                db_log = SentLog(email=email, to=subscription.email, result=4,
                                 log_message=u"Unknown error %s" % (str(e)))
                db_log.save()
                #blast_logger.error("%s - Unknown Failer %s" % (to_email.infoValue, e))
                print "%s - Unknown Failer %s" % (subscription.email, e)
        else:       
            #blast_logger.info(to_email.infoValue + " - Already Sent")
            print subscription.email + " - Already Sent"


    #blast_logger.info('Mailblast %s to %s is ended.' % (email.subject, listname))
    email.change_status(3)
    print 'Mailblast %s to %s is ended.' % (email.subject, listname)
    
    return True
