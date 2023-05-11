import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

from flask import Blueprint, render_template, render_template_string


def hello_plugin():
    '''A simple view function'''
    return u'Hello all, this is from ext1!!'

def hello_html_plugin():
    '''Render ext1 html function'''

    return render_template('ext1.html')

# def bootstrap_plugin():
#     '''Render bootstrap page'''
#     return render_template('index.html')

class Ext1Plugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IBlueprint)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, "templates")
        # toolkit.add_public_directory(config_, "public")
        toolkit.add_resource("assets", "style")

    # IBlueprint
    
    def get_blueprint(self):
        u'''Return a Flask Blueprint object to be registered by the app.'''
        
        # Create blueprint for plugin
        blueprint = Blueprint(self.name, self.__module__)
        blueprint.template_folder = 'templates'
        
        # Add plugin url rules to Blueprint object
        rules = [
            ('/hello_plugin', 'hello_plugin', hello_plugin),
            ('/hello_html_plugin', 'hello_html_plugin', hello_html_plugin),
            # ('/bootstrap_plugin', 'bootstrap_plugin', bootstrap_plugin),
        ]
        
        for rule in rules:
            blueprint.add_url_rule(*rule)
        
        return blueprint
    
