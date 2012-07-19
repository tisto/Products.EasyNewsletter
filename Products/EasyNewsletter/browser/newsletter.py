# -*- coding: utf-8 -*-
from AccessControl.SecurityManagement import newSecurityManager
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.EasyNewsletter import EasyNewsletterMessageFactory as _


class NewsletterView(BrowserView):
    """
    """

    confirm_email_template = ViewPageTemplateFile('change_email.pt')

    def unsubscribe(self):
        """
        """

        putils = getToolByName(self.context, "plone_utils")
        catalog = getToolByName(self.context, "reference_catalog")
        uid = self.request.get("subscriber")

        subscriber = catalog.lookupObject(uid)
        if subscriber is None:
            putils.addPortalMessage(_("An error occured"), "error")
        else:
            newsletter = self.context
            # We do the deletion as the owner of the newsletter object
            # so that this is possible without login.
            owner = newsletter.getWrappedOwner()
            newSecurityManager(newsletter, owner)
            del newsletter[subscriber.id]
            putils.addPortalMessage(_("You have been unsubscribed."))

        return self.request.response.redirect(self.context.absolute_url())

    def getRenderedIssues(self):
        """ Return the rendered body of all newsletter issues """

        result = list()
        catalog = getToolByName(self.context, "portal_catalog")
        for brain in catalog(portal_type='ENLIssue',
                             path='/'.join(self.context.getPhysicalPath())):
            issue = brain.getObject()
            content = issue.restrictedTraverse('@@get-public-body')()
            result.append(dict(content=content, title=issue.Title()))
        return result

    def confirm_newsletter(self):
        putils = getToolByName(self.context, "plone_utils")
        catalog = getToolByName(self.context, "reference_catalog")
        uid = self.request.get("subscriber")
        subscriber = catalog.lookupObject(uid)
        newsletter_url = self.context.absolute_url()
        if subscriber is None:
            putils.addPortalMessage(_("An error occured"), "error")
            return self.request.response.redirect(newsletter_url)

        subscriber.er_confirmed = True
        putils.addPortalMessage(u"Vielen Dank für das Abonnieren "
                                u"unseres Newsletters.")
        change_email_url = self.context.er_change_email_url(uid)
        return self.request.response.redirect(change_email_url)

    def change_email(self):
        putils = getToolByName(self.context, "plone_utils")
        catalog = getToolByName(self.context, "reference_catalog")
        registration_tool = getToolByName(self.context, 'portal_registration')

        uid = self.request.get("subscriber")
        subscriber = catalog.lookupObject(uid)
        newsletter_url = self.context.absolute_url()
        if subscriber is None:
            putils.addPortalMessage(("Es konnte kein passenes "
                                     "Newsletterabonnement gefunden werden."),
                                    "error")
            return self.request.response.redirect(newsletter_url)

        if self.request.method == 'POST':
            new_email = self.request.get("new", '').strip()
            if not registration_tool.isValidEmail(new_email):
                putils.addPortalMessage(
                    u'Bitte geben sie ein gültige E-Mail-Adresse an.',
                    'error')
                return self.confirm_email_template()

            subscriber.email = new_email
            putils.addPortalMessage(
                (u'Die E-Mail-Adresse wurde in geändert. '
                 u'Der Newsletter wir nun an „%s“ gesendet.') % new_email,
                'info')
            return self.request.response.redirect(newsletter_url)

        return self.confirm_email_template()
