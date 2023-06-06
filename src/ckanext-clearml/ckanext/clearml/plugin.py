import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import logging
from flask import Blueprint, render_template, render_template_string
from clearml import Dataset

def renderVersionTree():
    """
    Retrieve specified dataset's objects from ClearML, 
    and return the values through render_template to display on the frontend.

    Returns:
        render_template: 
            Returns the dictionary that stores the dependency graph,
            the list of IDs available from the specified dataset,
            and the details of the dataset tagged to its own ID in a dictionary.
    """
    palkia_dependency_graph = None
    dataset_IDs = []
    dataset_details = {}

    try:
        palkia_dataset = Dataset.get(
            dataset_project="Pokemon Project",
            dataset_name="dataset Pokemon",
            dataset_version="1.4"
        )
        palkia_dependency_graph = palkia_dataset.get_dependency_graph()
        for key, val in palkia_dependency_graph.items():
            logging.warning(f"key: {key}\tval: {val}")
            dataset_IDs.append(key)
    except Exception as e:
        logging.warning(f"FAILED TO GET DEPENDENCY GRAPH. ERROR: {e}")

    try:
        for each_id in dataset_IDs:
            dataset_details[each_id] = Dataset.get(
                dataset_id=each_id,
            )
            logging.warning(f"GETTING DATASET FOR ID {each_id} SUCCESS")
    except Exception as e:
        logging.warning(f"FAILED TO RETRIEVE DATASET OBJECTS FOR EACH DATASET. ERROR: {e}")

    
    return render_template('versionTree.html', palkia_dependency_graph=palkia_dependency_graph, dataset_IDs=dataset_IDs, dataset_details=dataset_details)

class ClearmlPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IBlueprint)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, "templates")
        toolkit.add_public_directory(config_, "public")
        toolkit.add_resource("assets", "clearml")

    def get_blueprint(self):
        blueprint = Blueprint(self.name, self.__module__)
        blueprint.template_folder = 'templates'

        rules = [
            ('/versiontree', 'versiontree', renderVersionTree), 
        ]

        for rule in rules:
            blueprint.add_url_rule(*rule)

        return blueprint
