from __future__ import annotations
import logging

from typing import Optional, cast
from ckan.types import AuthFunction, AuthResult, Context, ContextValidator, DataDict
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

from flask import Blueprint, render_template, request, jsonify


def getUserList():
    try:
        user_ids = toolkit.get_action('user_list')({}, {})
    except Exception as e:
        logging.warning("getUserList() Errorrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr")
        logging.warning(f"The error is {e}")
    logging.warning(f"Successfully requested user list")
    id_list = [u_id['id'] for u_id in user_ids]
    return id_list

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
        logging.warning(f"Printing results:")
        logging.warning(f"{result}")
        return render_template("userList.html", result=result)
    elif request.method == 'GET':
        userlist = getUserList()
        logging.warning(f"List of user id:")
        for id in userlist:
            logging.warning(f"id: {id}")
        # logging.warning(f"\n\n\nUSER LIST HERE: {userlist}\n\n\n")
        return render_template('userList.html', userlist=userlist, result=None)
    

def display_groups():
     if request.method == 'POST':
         return toolkit.redirect_to('/')
     elif request.method == 'GET':
        grouplist = getGroups()
        logging.warning(f"Group List:")
        for group in grouplist:
            logging.warning(f"{group}")
        return render_template('displayGroups.html', grouplist=grouplist)
     

class IauthfunctionsPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IBlueprint)
    
    
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
