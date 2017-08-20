# -*- coding: utf8 -*-
#
# Copyright (C) Cauly Kan, mail: cauliflower.kan@gmail.com
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.

from trac.core import Component, implements
from tracrpc.api import IXMLRPCHandler
from trac.perm import PermissionSystem


class TracRpcGetAllUsers(Component):
    implements(IXMLRPCHandler)

    def __init__(self):
        pass

    def xmlrpc_namespace(self):
        return 'user'

    def xmlrpc_methods(self):
        yield 'WIKI_VIEW', ((dict,),), self.getAllUsers
        yield 'WIKI_VIEW', ((dict,),), self.getAllUserGroups
        yield 'WIKI_VIEW', ((list,),), self.getAllPermissions
        yield 'WIKI_VIEW', ((dict, str),), self.resolveUsers

    def getAllUsers(self, req):
        """
            Get all known users.
        """

        return self.env.get_known_users(True)

    def getAllUserGroups(self, req):
        """
            Get all user groups.
        """

        ps = PermissionSystem(self.env)

        return ps.get_groups_dict()

    def getAllPermissions(self, req):
        """
            Get all permission names.
        """

        ps = PermissionSystem(self.env)

        result = [x[0] for x in ps.get_all_permissions()]
        result.extend(ps.get_actions())

        return set(result)

    def resolveUsers(self, req, users_perms_and_groups):
        """
            Get a user list for a given string, representing groups or permissions.
        """

        ps = PermissionSystem(self.env)
        groups = ps.get_groups_dict()

        def append_owners(users_perms_and_groups):
            for user_perm_or_group in users_perms_and_groups:
                if user_perm_or_group == 'authenticated':
                    owners.update(set(u[0] for u in self.env.get_known_users()))
                elif user_perm_or_group.isupper():
                    perm = user_perm_or_group
                    for user in ps.get_users_with_permission(perm):
                        owners.add(user)
                elif user_perm_or_group not in groups:
                    owners.add(user_perm_or_group)
                else:
                    append_owners(groups[user_perm_or_group])

        owners = set()
        append_owners(users_perms_and_groups)

        return sorted(owners)