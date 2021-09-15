from __future__ import absolute_import, unicode_literals

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.urls import reverse, reverse_lazy
from django.utils.translation import ungettext, ugettext_lazy as _

from mayan.apps.common.views import (
    AssignRemoveView, MultipleObjectConfirmActionView,
    MultipleObjectFormActionView, SingleObjectCreateView,
    SingleObjectDeleteView, SingleObjectDetailView, SingleObjectEditView,
    SingleObjectListView
)

from .events import (
    event_group_created, event_group_edited, event_user_created,
    event_user_edited
)
from .forms import UserForm
from .icons import icon_group_setup, icon_user_setup
from .links import link_group_create, link_user_create
from .permissions import (
    permission_group_create, permission_group_delete, permission_group_edit,
    permission_group_view, permission_user_create, permission_user_delete,
    permission_user_edit, permission_user_view
)


class CurrentUserDetailsView(SingleObjectDetailView):
    fields = (
        'username', 'first_name', 'last_name', 'email', 'last_login',
        'date_joined', 'groups'
    )

    def get_object(self):
        return self.request.user

    def get_extra_context(self, **kwargs):
        return {
            'object': None,
            'title': _('Current user details'),
        }


class CurrentUserEditView(SingleObjectEditView):
    extra_context = {'object': None, 'title': _('Edit current user details')}
    form_class = UserForm
    post_action_redirect = reverse_lazy('user_management:current_user_details')

    def get_object(self):
        return self.request.user


class GroupCreateView(SingleObjectCreateView):
    extra_context = {'title': _('Create new group')}
    fields = ('name',)
    model = Group
    post_action_redirect = reverse_lazy('user_management:group_list')
    view_permission = permission_group_create

    def form_valid(self, form):
        group = form.save()

        event_group_created.commit(
            actor=self.request.user, target=group
        )

        messages.success(
            self.request, _('Group "%s" created successfully.') % group
        )
        return super(GroupCreateView, self).form_valid(form=form)


class GroupEditView(SingleObjectEditView):
    fields = ('name',)
    model = Group
    object_permission = permission_group_edit
    post_action_redirect = reverse_lazy('user_management:group_list')

    def form_valid(self, form):
        event_group_edited.commit(
            actor=self.request.user, target=self.get_object()
        )
        return super(GroupEditView, self).form_valid(form=form)

    def get_extra_context(self):
        return {
            'object': self.get_object(),
            'title': _('Edit group: %s') % self.get_object(),
        }


class GroupListView(SingleObjectListView):
    model = Group
    object_permission = permission_group_view

    def get_extra_context(self):
        return {
            'hide_object': True,
            'no_results_icon': icon_group_setup,
            'no_results_main_link': link_group_create.resolve(
                context=RequestContext(request=self.request)
            ),
            'no_results_text': _(
                'User groups are organizational units. They should '
                'mirror the organizational units of your organization. '
                'Groups can\'t be used for access control. Use roles '
                'for permissions and access control, add groups to '
                'them.'
            ),
            'no_results_title': _('There are no user groups'),
            'title': _('Groups'),
        }


class GroupDeleteView(SingleObjectDeleteView):
    model = Group
    object_permission = permission_group_delete
    post_action_redirect = reverse_lazy('user_management:group_list')

    def get_extra_context(self):
        return {
            'object': self.get_object(),
            'title': _('Delete the group: %s?') % self.get_object(),
        }


class GroupMembersView(AssignRemoveView):
    decode_content_type = True
    left_list_title = _('Available users')
    right_list_title = _('Users in group')
    object_permission = permission_group_edit

    @staticmethod
    def generate_choices(choices):
        results = []
        for choice in choices:
            ct = ContentType.objects.get_for_model(choice)
            label = choice.get_full_name() if choice.get_full_name() else choice

            results.append(('%s,%s' % (ct.model, choice.pk), '%s' % (label)))

        # Sort results by the label not the key value
        return sorted(results, key=lambda x: x[1])

    def add(self, item):
        self.get_object().user_set.add(item)

    def get_extra_context(self):
        return {
            'object': self.get_object(),
            'title': _('Users of group: %s') % self.get_object()
        }

    def get_object(self):
        return get_object_or_404(klass=Group, pk=self.kwargs['pk'])

    def left_list(self):
        return GroupMembersView.generate_choices(
            get_user_model().objects.exclude(
                groups=self.get_object()
            ).exclude(is_staff=True).exclude(is_superuser=True)
        )

    def right_list(self):
        return GroupMembersView.generate_choices(
            self.get_object().user_set.all()
        )

    def remove(self, item):
        self.get_object().user_set.remove(item)


class UserCreateView(SingleObjectCreateView):
    extra_context = {
        'title': _('Create new user'),
    }
    form_class = UserForm
    view_permission = permission_user_create

    def form_valid(self, form):
        user = form.save(commit=False)
        user.set_unusable_password()
        user.save()

        event_user_created.commit(
            actor=self.request.user, target=user
        )

        messages.success(
            self.request, _('User "%s" created successfully.') % user
        )
        return HttpResponseRedirect(
            reverse('user_management:user_set_password', args=(user.pk,))
        )


class UserDeleteView(MultipleObjectConfirmActionView):
    object_permission = permission_user_delete
    queryset = get_user_model().objects.filter(
        is_superuser=False, is_staff=False
    )
    success_message = _('User delete request performed on %(count)d user')
    success_message_plural = _(
        'User delete request performed on %(count)d users'
    )

    def get_extra_context(self):
        queryset = self.get_queryset()

        result = {
            'title': ungettext(
                'Delete user',
                'Delete users',
                queryset.count()
            )
        }

        if queryset.count() == 1:
            result.update(
                {
                    'object': queryset.first(),
                    'title': _('Delete user: %s') % queryset.first()
                }
            )

        return result

    def object_action(self, form, instance):
        try:
            if instance.is_superuser or instance.is_staff:
                messages.error(
                    self.request,
                    _(
                        'Super user and staff user deleting is not '
                        'allowed, use the admin interface for these cases.'
                    )
                )
            else:
                instance.delete()
                messages.success(
                    self.request, _(
                        'User "%s" deleted successfully.'
                    ) % instance
                )
        except Exception as exception:
            messages.error(
                self.request, _(
                    'Error deleting user "%(user)s": %(error)s'
                ) % {'user': instance, 'error': exception}
            )


class UserDetailsView(SingleObjectDetailView):
    fields = (
        'username', 'first_name', 'last_name', 'email', 'last_login',
        'date_joined', 'groups',
    )
    object_permission = permission_user_view
    queryset = get_user_model().objects.filter(
        is_superuser=False, is_staff=False
    )

    def get_extra_context(self, **kwargs):
        return {
            'object': self.get_object(),
            'title': _('Details of user: %s') % self.get_object()
        }


class UserEditView(SingleObjectEditView):
    fields = ('username', 'first_name', 'last_name', 'email', 'is_active',)
    object_permission = permission_user_edit
    post_action_redirect = reverse_lazy('user_management:user_list')
    queryset = get_user_model().objects.filter(
        is_superuser=False, is_staff=False
    )

    def form_valid(self, form):
        event_user_edited.commit(
            actor=self.request.user, target=self.get_object()
        )
        return super(UserEditView, self).form_valid(form=form)

    def get_extra_context(self):
        return {
            'object': self.get_object(),
            'title': _('Edit user: %s') % self.get_object(),
        }


class UserGroupsView(AssignRemoveView):
    decode_content_type = True
    left_list_title = _('Available groups')
    right_list_title = _('Groups joined')
    object_permission = permission_user_edit

    def add(self, item):
        item.user_set.add(self.get_object())

    def get_extra_context(self):
        return {
            'object': self.get_object(),
            'title': _('Groups of user: %s') % self.get_object()
        }

    def get_object(self):
        return get_object_or_404(
            klass=get_user_model().objects.filter(
                is_superuser=False, is_staff=False
            ), pk=self.kwargs['pk']
        )

    def left_list(self):
        return AssignRemoveView.generate_choices(
            Group.objects.exclude(user=self.get_object())
        )

    def right_list(self):
        return AssignRemoveView.generate_choices(
            Group.objects.filter(user=self.get_object())
        )

    def remove(self, item):
        item.user_set.remove(self.get_object())


class UserListView(SingleObjectListView):
    object_permission = permission_user_view

    def get_extra_context(self):
        return {
            'hide_object': True,
            'no_results_icon': icon_user_setup,
            'no_results_main_link': link_user_create.resolve(
                context=RequestContext(request=self.request)
            ),
            'no_results_text': _(
                'User accounts can be create from this view. After creating '
                'an user account you will prompted to set a password for it. '
            ),
            'no_results_title': _('There are no user accounts'),
            'title': _('Users'),
        }

    def get_object_list(self):
        return get_user_model().objects.exclude(
            is_superuser=True
        ).exclude(is_staff=True).order_by('last_name', 'first_name')


class UserOptionsEditView(SingleObjectEditView):
    fields = ('block_password_change',)
    object_permission = permission_user_edit

    def get_extra_context(self):
        return {
            'object': self.get_user(),
            'title': _(
                'Edit options for user: %s'
            ) % self.get_user()
        }

    def get_object(self, queryset=None):
        return self.get_user().user_options

    def get_post_action_redirect(self):
        return reverse('user_management:user_list')

    def get_user(self):
        return get_object_or_404(
            klass=get_user_model().objects.filter(
                is_superuser=False, is_staff=False
            ), pk=self.kwargs['pk']
        )


class UserSetPasswordView(MultipleObjectFormActionView):
    form_class = SetPasswordForm
    model = get_user_model()
    object_permission = permission_user_edit
    success_message = _('Password change request performed on %(count)d user')
    success_message_plural = _(
        'Password change request performed on %(count)d users'
    )

    def get_extra_context(self):
        queryset = self.get_queryset()

        result = {
            'submit_label': _('Submit'),
            'title': ungettext(
                'Change user password',
                'Change users passwords',
                queryset.count()
            )
        }

        if queryset.count() == 1:
            result.update(
                {
                    'object': queryset.first(),
                    'title': _('Change password for user: %s') % queryset.first()
                }
            )

        return result

    def get_form_extra_kwargs(self):
        queryset = self.get_queryset()
        result = {}
        if queryset:
            result['user'] = queryset.first()
            return result
        else:
            raise PermissionDenied

    def object_action(self, form, instance):
        try:
            if instance.is_superuser or instance.is_staff:
                messages.error(
                    self.request,
                    _(
                        'Super user and staff user password '
                        'reseting is not allowed, use the admin '
                        'interface for these cases.'
                    )
                )
            else:
                instance.set_password(form.cleaned_data['new_password1'])
                instance.save()
                messages.success(
                    self.request, _(
                        'Successful password reset for user: %s.'
                    ) % instance
                )
        except Exception as exception:
            messages.error(
                self.request, _(
                    'Error reseting password for user "%(user)s": %(error)s'
                ) % {
                    'user': instance, 'error': exception
                }
            )
