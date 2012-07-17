from AccessControl.SecurityManagement import newSecurityManager
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView

from Products.EasyNewsletter import EasyNewsletterMessageFactory as _


class NewsletterView(BrowserView):
    """
    """

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

        confirmed = getattr(subscriber, 'er_confirmed', False)
        if confirmed:
            putils.addPortalMessage(
                _("Your E-Mail-Adress is already confirmed."))
            return self.request.response.redirect(newsletter_url)
        else:
            subscriber.er_confirmed = True
            putils.addPortalMessage(_("You have confirmed the email address."))
            change_email_url = self.context.er_change_email_url(uid)
            return self.request.response.redirect(change_email_url)
