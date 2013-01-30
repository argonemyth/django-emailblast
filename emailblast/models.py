# coding=utf-8
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

from datetime import datetime
from emailblast import settings


class Newsletter(models.Model):
    """
    A newsletter we can send to contacts.
    It manages the subscribers.
    """
    title = models.CharField(_('newsletter title'), max_length=200)
    slug = models.SlugField(db_index=True, unique=True)
    active = models.BooleanField(_('active'), default=True)
    template = models.CharField(max_length=100, blank=True, default="default", 
                                help_text=_("Name of of the template, which you will need to create under templates/emailblast"))
    use_html = models.BooleanField(_('Use HTML?'), default=True)
     
    sender_name = models.CharField(_('sender name'), max_length=200)
    sender_email = models.EmailField(_('sender e-mail'))
    reply_email = models.EmailField(_("reply-to"), blank=True)

    date_create = models.DateTimeField(_('creation date'), auto_now_add=True)
    date_modify = models.DateTimeField(_('modification date'), auto_now=True)

    # Fields below are for later
    #site = models.ForeignKey(Site, verbose_name=_("site"), related_name="newsletters", default=1)
    #language = models.CharField(max_length=6, verbose_name=_("language"), choices=settings.LANGUAGES)

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = _('newsletter')
        verbose_name_plural = _('newsletters')

    @models.permalink
    def get_absolute_url(self):
        return ('newsletter_detail', (),
                {'newsletter_slug': self.slug })

    @models.permalink
    def subscribe_url(self):
        return ('newsletter_subscribe_request', (),
                {'newsletter_slug': self.slug })

    @models.permalink
    def unsubscribe_url(self):
        return ('newsletter_unsubscribe_request', (),
                {'newsletter_slug': self.slug })

    @models.permalink
    def update_url(self):
        return ('newsletter_update_request', (),
                {'newsletter_slug': self.slug })

    def get_sender(self):
        return u'%s <%s>' % (self.sender_name, self.sender_email)

    def get_templates(self):
        temp_name = self.template.lower()
        if self.use_html:
            return "emailblast/" + temp_name + ".html", "emailblast/" + temp_name + ".txt"
        else:
            return None, "emailblast/" + temp_name + ".txt"
        
        
class Subscription(models.Model):
    """
    A individual subscription from a human being, could be an user,
    or just a name and email. We are not going to keep tracking
    user's subscription activity.
    """
    user = models.ForeignKey(User, blank=True, null=True, verbose_name=_('user'), related_name="emails")
    newsletter = models.ForeignKey('Newsletter', verbose_name=_('newsletter'), related_name="subscription")
    name_field = models.CharField(db_column='name', max_length=100, blank=True, null=True, 
                                 verbose_name=_('name'), help_text=_('optional'))
    def get_name(self):
        if self.user:
            return self.user.get_full_name()
        return self.name_field
    def set_name(self, name):
        if not self.user:
            self.name_field = name
    name = property(get_name, set_name)

    email_field = models.EmailField(db_column='email', verbose_name=_('e-mail'), db_index=True, blank=True, null=True)
    def get_email(self):
        if self.user:
            return self.user.email
        return self.email_field
    def set_email(self, email):
        if not self.user:
            self.email_field = email
    email = property(get_email, set_email) 
    
    date_create = models.DateTimeField(editable=False, default=datetime.now)
    # When user changed setting in user profile
    subscribed = models.BooleanField(_('subscribed'), default=True, db_index=True)

    class Meta:
        verbose_name = _('subscription')
        verbose_name_plural = _('subscriptions')
        unique_together = ('user', 'email_field', 'newsletter') 
    
    def __unicode__(self):
        if self.name:
            return _(u"%(name)s <%(email)s> to %(newsletter)s") % {'name':self.name, 'email':self.email, 'newsletter':self.newsletter}
        else:
            return _(u"%(email)s to %(newsletter)s") % {'email':self.email, 'newsletter':self.newsletter}
    
    def save(self, *args, **kwargs):
        assert self.user or self.email_field, _('Neither an email nor a username is set.')
        assert (self.user and not self.email_field) or (self.email_field and not self.user), _('If user is set, email must be null and vice versa.')

        super(Subscription, self).save(*args, **kwargs) 
     
    @models.permalink
    def get_absolute_url(self):
        pass

    def subscribe(self):
        #logger.debug(u'Subscribing subscription %s.', self)
        self.subscribed = True
        self.save()

    def unsubscribe(self):
        #logger.debug(u'Unsubscribing subscription %s.', self)
        self.subscribed = False
        self.save()

    def get_recipient(self):
        if self.name:
            return u'%s <%s>' % (self.name, self.email)

        return u'%s' % (self.email)


class Email(models.Model):
    """
    An individual email that will be sent out. 
    """
    DRAFT = 0
    WAITING = 1
    SENDING = 2
    SENT = 3
    CANCELED = 4

    STAT_CODE = (
        (DRAFT, _('draft')), 
        (WAITING, _('waiting')),
        (SENDING, _("sending")),
        (SENT, _("sent")),
        (CANCELED, _("canceled")),
    )   

    newsletter = models.ForeignKey('Newsletter', verbose_name=_('newsletter'), related_name="emails", null=True)
    subject = models.CharField( _("Subject"), max_length=100 )
    slug = models.SlugField(verbose_name=_('slug'))
    composer = models.ForeignKey(User, related_name="sent_emails")
    
    content = models.TextField( _("content"), null=True, blank=True, help_text=_("Content of your email; ") )
    url = models.URLField(verbose_name=_('link'), blank=True, null=True, verify_exists=False) 
    image = models.ImageField( _("image"), upload_to="newsletter/images", null=True, blank=True)
    attachment = models.FileField( _("attachment"), upload_to="newsletter/files", null=True, blank=True, help_text=_("Attach pdf or other document if necessary.") )

    status = models.PositiveSmallIntegerField(_('status'), choices=STAT_CODE, default=DRAFT) 
    date_create = models.DateTimeField(_('created'), auto_now_add=True, editable=False)
    date_modify = models.DateTimeField(_('modified'), auto_now=True, editable=False)
    
    class Meta:
        verbose_name = _('email')
        verbose_name_plural = _('emails')
        unique_together = ("slug", "newsletter")
        ordering = ('-date_create',)
        
    def __unicode__(self):
        try:
            return _(u"%(subject)s in %(newsletter)s") % {'subject':self.subject, 'newsletter':self.newsletter}
        except Newsletter.DoesNotExist:
            logger.warn('Database inconsistency, related newsletter not found for message with id %d', self.id)

            return "%s" % self.subject
    
    def change_status(self, status_code):
        self.status = status_code
        self.save()
 
    @models.permalink
    def preview_html(self):
        return ('email_preview', (), {'slug': self.slug, 'format': "html"})

    @models.permalink
    def preview_text(self):
        return ('email_preview', (), {'slug': self.slug, 'format': "txt"})

    @models.permalink
    def get_absolute_url(self):
        return ('view_email', (), {'slug': self.slug})


class SentLog(models.Model):
    """
    The result of email sending process.
    """
    RESULT_CODES = ( 
        (1, _("success")),
        (2, _("failure")),
        (3, _("skipped - in blacklist")),
        (4, _("unknown failure")),
    )   

    email = models.ForeignKey(Email, related_name="send_log")
    to = models.EmailField()
    result = models.PositiveSmallIntegerField(choices=RESULT_CODES)
    timestamp = models.DateTimeField(auto_now_add=True, editable=False)
    log_message = models.TextField(null=True, blank=True)

    def __unicode__(self):
        return u"%s to %s is %s" % (self.email, self.to, self.get_result_display())

    class Meta:
        ordering = ['-timestamp'] # - indicates descending order
