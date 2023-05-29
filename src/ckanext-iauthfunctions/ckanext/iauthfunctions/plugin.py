from __future__ import annotations
import logging
import ast
from typing import Any, Optional, cast
from ckan.types import AuthFunction, AuthResult, Context, ContextValidator, DataDict
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

from flask import Blueprint, render_template, request, jsonify


def getUserList():
    user_ids = None
    try:
        user_ids = toolkit.get_action('user_list')({}, {'all_fields': True, 'include_site_user': True})
    except Exception as e:
        logging.warning("getUserList() Errorrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr")
        logging.warning(f"The error is {e}")
    logging.warning(f"Successfully requested user list")
    logging.warning(f"Printing full user list: {user_ids}")
    all_users = []
    
    for user in user_ids:
        user_details = {}
        user_details['id'] = user['id']
        user_details['name'] = user['name']
        user_details['sysadmin'] = user['sysadmin']
        all_users.append(user_details)
    # id_list = [u_id['id'] for u_id in user_ids]
    return all_users

def getGroups():
    groups = None
    try: 
        groups = toolkit.get_action('group_list')({}, {})
    except Exception as e:
        logging.warning("getGroups() ERRRRRORRRRRRRRRRRRRRRRRRRRRRRRRRRRRR")
        logging.warning(f"The error is {e}")
    logging.warning(f"Successfully requested group list")
    return groups

def process_request(data):
    """
    This function handles post request to create a group. 
    You must be logged in as a user first before you can create a group or
    you will receive an authentication error. 

    Args:
        data (Dict):  
            This dictionary is a parameter passed in from 
            create_group() inside the Plugin Class.
            The dictionary stores the form data that was filled in in the UI.
            For example, creating a group requires a name, title, description.
            The dictionary contains:
            {
                'name': data['name'], 
                'title': data['title'],
                'description': data['description']
            }

    Returns:
        Group Object: 
            This function returns the group object that was just created.
            It stores all the information that is created
            when the API function group_create() is called.
    """
    logging.warning("PRINTING DATA:")
    for key, val in data.items():
        logging.warning(f"{key} : {val}")
    logging.warning("POSTING GROUP CREATION NOWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW")
    if data['editType'] == 'create':
        try:
            group_created = toolkit.get_action('group_create')(
                {}, 
                {
                    'name': data['name'], 
                    'title': data['title'], 
                    'description': data['description']
                })
            logging.warning(f"")
            logging.warning(f"Group created variable: {type(group_created)}")
            logging.warning(f"")
            new_membership = None
            try:
                new_membership = toolkit.get_action('group_member_create')({}, {
                    'id': data['name'], 
                    'username': data['username'], 
                    'role': 'admin'
                })
                logging.warning(f"PRINTING NEW MEMBERSHIP DETAILS: {new_membership}")
            except Exception as e:
                logging.warning(f"Member Creation error: {e}")
            data = {
                'group_created': group_created, 
                'site_user': data['username'], 
                'new_membership': new_membership
            }
            return data
        except Exception as e:
            logging.warning(f"EXCEPTION ERROR: {e}")
    elif data['editType'] == 'edit':
        try:
            group_created = toolkit.get_action('group_patch')(
                {}, 
                {
                    'id': data['name'], 
                    'title': data['title'], 
                    'description': data['description']
                })
            logging.warning(f"")
            logging.warning(f"Group created variable: {type(group_created)}")
            logging.warning(f"")
            usernames = ast.literal_eval(data['username'])
            for username in usernames:
                try: 
                    new_membership = toolkit.get_action('member_create')({}, {
                        'id': data['name'], 
                        'object': username, 
                        'object_type': 'user',
                        'capacity': 'admin'
                    })
                    logging.warning(f"PRINTING NEW MEMBERSHIP DETAILS: {new_membership}")
                except Exception as e:
                    logging.warning(f"ERROR HIT WHEN EDITING GROUP: TRYING TO CREATE NEW MEMBER: \n{e}")
            return group_created
        except Exception as e:
            logging.warning(f"EXCEPTION ERROR: {e}")

def create_group():
    """
    This function renders the template of the group_create form.
    If it is performing a POST request (when the form is submitted), 
    it will display the new group that is just created. 

    Returns:
        render_template: 
        it will either return the form to create group, 
        together with a current list of user id, 
        or 
        to render the same form to create group, 
        together with the new group that was just created.
    """
    
    if request.method == 'POST':
        data = request.form
        result = process_request(data)
        logging.warning(f"Printing resultsssss:")
        for key, val in data.items():
            logging.warning(f"{key} : {val}")
        return render_template("userList.html", result=result, group_details=None)
    elif request.method == 'GET':
        userlist = getUserList()
        logging.warning(f"List of user id:")
        for user in userlist:
            for key, val in user.items():
                logging.warning(f"user id: {user['id']}")
                logging.warning(f"user name: {user['name']}")
                logging.warning(f"admin status: {user['sysadmin']}")
        # logging.warning(f"\n\n\nUSER LIST HERE: {userlist}\n\n\n")
        return render_template('userList.html', userlist=userlist, result=None, group_details=None)
    

def display_groups():
    if request.method == 'POST':
        group_obj = request.form.to_dict()
        logging.warning(f"")
        logging.warning(f"")
        group_name = group_obj['groupname']
        logging.warning(f"Grouppp Object: {group_obj}")

        group_details = None
        try: 
            
            logging.warning(f"")
            logging.warning(f"Group name: {group_name}")
            logging.warning(f"")
            group_details = toolkit.get_action('group_list')({}, {
                'groups': [group_name], 
                'all_fields': True,
            })
        except Exception as e:
            logging.warning("FAILED API QUERY: ERROR IS ")
            logging.warning(f"{e}")
            logging.warning("")
        logging.warning(f"Group details: {group_details}")
        logging.warning(f"")
        try: 
            member_list = toolkit.get_action('member_list')({}, {'id': group_name, 'object_type': 'user'})
        except Exception as e:
            logging.warning(f"UNABLE TO GET MEMBER LIST - ERROR: {e}")
        group_details[0]['member_list'] = [member_id[0] for member_id in member_list]
        userlist = getUserList()
        return render_template('userList.html', userlist=userlist, group_details=group_details, result=None)
    elif request.method == 'GET':
        grouplist = getGroups()
        logging.warning(f"Group List:")
        for group in grouplist:
            logging.warning(f"{group}")
        return render_template('displayGroups.html', grouplist=grouplist)


def group_patch(context: Context, data_dict: Optional[dict[str, Any]] = None) -> AuthResult:
    logging.warning(f"This is going through authorizationnnnnnnnnnnnnnnnnnnnnnnnnn")
    # Get the user name of the logged-in user.
    user_name = context['user']

    # Get a list of the members of the 'curators' group.
    try:
        members = toolkit.get_action('member_list')(
            {},
            {'id': data_dict['id'], 'object_type': 'user'})
    except toolkit.ObjectNotFound:
        # The curators group doesn't exist.
        return {'success': False,
                'msg': "The group does not exist, so only sysadmins "
                       "are authorized to create groups."}

    # 'members' is a list of (user_id, object_type, capacity) tuples, we're
    # only interested in the user_ids.
    member_ids = [member_tuple[0] for member_tuple in members]
    logging.warning(f"Printing member list: \n{members}\n{member_ids}")
    # We have the logged-in user's user name, get their user id.
    convert_user_name_or_id_to_id = cast(
        ContextValidator,
        toolkit.get_converter('convert_user_name_or_id_to_id'))
    try:
        user_id = convert_user_name_or_id_to_id(user_name, context)
    except toolkit.Invalid:
        # The user doesn't exist (e.g. they're not logged-in).
        return {'success': False,
                'msg': 'You must be logged-in as a member of the '
                       'group to create new groups.'}

    # Finally, we can test whether the user is a member of the curators group.
    if user_id in member_ids:
        return {'success': True}
    else:
        return {'success': False,
                'msg': 'Only admins and members of the group are allowed to create groups'}

class IauthfunctionsPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IBlueprint)
    plugins.implements(plugins.IAuthFunctions)
    
    def get_auth_functions(self):
        return {'group_patch': group_patch}
    # IConfigurer
    def update_config(self, config_):
        toolkit.add_template_directory(config_, "templates")
        toolkit.add_public_directory(config_, "public")
        toolkit.add_resource("assets", "iauthfunctions")

    # IBlueprint
    def get_blueprint(self):
        """
        This function registers the blueprints to display different html pages. 
        it creates the blueprint object, 
        then register the url that will be used to display the HTML page, 
        along with the name to label it and the function that calls render_template.

        This will be registered in a rule and 
        we will use the blueprint object to add the rule as a url.

        Returns:
            Blueprint object: 
            It returns the blueprint that does wtv flask uses it for. 
            Don't really understand it ngl.
        """
        blueprint = Blueprint(self.name, self.__module__)
        blueprint.template_folder = 'templates'

        rules = [
            ('/listOfUsers', 'listOfUsers', create_group), 
            ('/displayGroups', 'displayGroups', display_groups),
        ]    

        for rule in rules:
            blueprint.add_url_rule(*rule, methods=['POST', 'GET'])

        return blueprint
