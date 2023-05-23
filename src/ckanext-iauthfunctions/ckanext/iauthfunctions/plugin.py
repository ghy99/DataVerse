from __future__ import annotations
import logging

from typing import Optional, cast
from ckan.types import AuthFunction, AuthResult, Context, ContextValidator, DataDict
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

from flask import Blueprint, render_template


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


# def group_create(context:Context, data_dict: Optional[DataDict] = None) ->AuthResult:
#     user_name: str = context['user']
#     try:
#         members = toolkit.get_action('user_list')(
#             {}, 
#             {}
#         )
#     except:
#         return {'success': False, 'msg': "LALALALALALALALALALALALAThe unable to get user list."}
#     # member_ids = [member_tuple[0] for member_tuple in members]
#     user_ids = [u_id['id'] for u_id in members]
#     logging.warning(f"USER LIST HERE AHHHHHHHHHHHHH: {user_ids}")
#     for i in user_ids:
#         print(f"ID: {i}")
#     convert_user_name_or_id_to_id = cast(
#         ContextValidator, 
#         toolkit.get_converter('convert_user_name_or_id_to_id')
#     )
#     try:
#         user_id = convert_user_name_or_id_to_id(user_name, context)
#     except toolkit.Invalid:
#         return {'success': False, 'msg': 'You must be logged in as a member of the curators group to create groups bruh'}
    

#     if user_id in user_ids:
#         return {'success': True}
#     else:
#         return {'success': False, 'msg':'Only myGroup people are allowed to create groups'}
    

class IauthfunctionsPlugin(plugins.SingletonPlugin):
    # plugins.implements(plugins.IAuthFunctions)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IBlueprint)

    def get_helpers(self):
        return {'getUserList': getUserList}
    
    # def get_auth_functions(self) -> dict[str, AuthFunction]:
    #     return {'group_create' : group_create}
    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, "templates")
        toolkit.add_public_directory(config_, "public")
        toolkit.add_resource("assets", "iauthfunctions")

    def get_blueprint(self):
        blueprint = Blueprint(self.name, self.__module__)
        blueprint.template_folder = 'templates'

        rules = [
            ('/listOfUsers', 'listOfUsers', listOfUsers),
        ]    

        for rule in rules:
            blueprint.add_url_rule(*rule)

        return blueprint
