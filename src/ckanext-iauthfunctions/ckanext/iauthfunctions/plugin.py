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
    except:
        logging.warning("Errorrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr")
        return 

    logging.warning("Successful get action?")

    id_list = [u_id['id'] for u_id in user_ids]
    return id_list


def listOfUsers():
    logging.warning("hello worlddddd")
    userlist = getUserList()
    logging.warning(f"List of user id:")
    for id in userlist:
        logging.warning(f"id: {id}")
    # logging.warning(f"\n\n\nUSER LIST HERE: {userlist}\n\n\n")
    return render_template('userList.html', result=userlist)

def process_request(data, context):
    logging.warning("PRINTING CONTEXT:")
    logging.warning(f"Context: {context}")
    logging.warning("PRINTING DATA:")
    for key, val in data.items():
        logging.warning(f"{key} : {val}")
    logging.warning("")
    logging.warning("")
    logging.warning("POSTING GROUP CREATION NOWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW")
    # user_name = context['user']
    try:
        group_created = toolkit.get_action('group_create')(
            {

            }, 
            {
                'name': data['name'], 
                'title': data['title'], 
                'description': data['description']
            })
        return group_created
    except Exception as e:
        logging.warning("")
        logging.warning("")
        logging.warning(f"EXCEPTION ERROR: {e}")
        logging.warning("")
        logging.warning("")



class IauthfunctionsPlugin(plugins.SingletonPlugin):
    # plugins.implements(plugins.IAuthFunctions)
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IBlueprint)
    
    # def get_auth_functions(self) -> dict[str, AuthFunction]:
    #     return {
    #         'group_create' : group_create}

    # IConfigurer


    def update_config(self, config_):
        toolkit.add_template_directory(config_, "templates")
        toolkit.add_public_directory(config_, "public")
        toolkit.add_resource("assets", "iauthfunctions")

    def get_blueprint(self):
        blueprint = Blueprint(self.name, self.__module__)
        blueprint.template_folder = 'templates'

        @blueprint.route('/listOfUsers/new', methods=['POST'])
        def create_group(context: Context):
            if request.method == 'POST':
                data = request.form
            result = process_request(data, context)

            return jsonify(result)

        rules = [
            ('/listOfUsers', 'listOfUsers', listOfUsers),
            ('/listOfUsers/new', 'listOfUsers/new', create_group),
        ]    

        for rule in rules:
            blueprint.add_url_rule(*rule)

        return blueprint
