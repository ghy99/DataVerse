import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

from flask import Blueprint, render_template, render_template_string

def myfirstplugin():
    return u'Welcome to Ba Sing Se!!!!!!!!!!!'

def teethplugin():
    return render_template('test.html')


class HaoyiPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IBlueprint)
    
    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, "templates")
        toolkit.add_public_directory(config_, "public")
        toolkit.add_resource("assets", "haoyi")

    # IBlueprint

    def get_blueprint(self):
        u'''Return a Flask Blueprint object to be registered by the app.'''
        
        # Create blueprint for plugin
        blueprint = Blueprint(self.name, self.__module__)
        blueprint.template_folder = 'templates'
        
        # Add plugin url rules to Blueprint object
        rules = [
            ('/myfirstplugin', 'myfirstplugin', myfirstplugin),
            ('/teethplugin', 'teethplugin', teethplugin),
            # ('/hello_html_plugin', 'hello_html_plugin', hello_html_plugin),
            # ('/bootstrap_plugin', 'bootstrap_plugin', bootstrap_plugin),
        ]
        
        for rule in rules:
            blueprint.add_url_rule(*rule)
        
        return blueprint
