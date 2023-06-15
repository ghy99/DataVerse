import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

from logging import warning
from flask import Blueprint, render_template
from clearml import Dataset


def getDataset():
    """
    This function retrieves the dataset object specified from ClearML.

    Returns:
        Dataset object: 
            Returns the specified Dataset object.
    """
    palkia_dataset = None
    try:
        palkia_dataset = Dataset.get(
            dataset_project="Pokemon Project",
            dataset_name="dataset Pokemon",
            dataset_version="1.4",
        )
    except Exception as e:
        warning(f"COULD NOT GET DATASET: ERROR: {e}")
    return palkia_dataset

def getDependencyGraph(dataset):
    """
    This function gets the dependency graph of the 
    dataset parameter that was passed in.

    Args:
        dataset (Dataset): 
            This is the Dataset object that was retrieved in the getDataset() function.

    Returns:
        Dictionary: { key (str): val (list) }
            The key refers to a Dataset ID, 
            The val refers to a list of Dataset IDs that are the parent of the key.
    """
    try:
        palkia_dependency_graph = dataset.get_dependency_graph()
        warning(palkia_dependency_graph)
    except Exception as e:
        warning(f"FAILED TO GET DEPENDENCY GRAPH. ERROR: {e}")
    return palkia_dependency_graph

def getAllDatasetID(dataset_id):
    try:
        dataset = Dataset.get(dataset_id=dataset_id)
    except Exception as e:
        warning(f"FAILED TO RETRIEVE DATASET {dataset_id}, ERROR: {e}")
    return dataset

def sortDataset(dataset_IDs, dataset_details):
    """
    Returns a sorted list of ID

    Args:
        dataset_IDs (list): list of dataset ID unsorted
        dataset_details (dict): Dictionary of each dataset ID tied to its ID as a key

    Returns:
        list: List of sorted Dataset ID
    """
    versions = []
    for each_ID in dataset_IDs:
        versions.append(dataset_details[each_ID]._dataset_version)

    # warning(f"Version list: {versions}, Sorted Version List: {sorted(versions)}")
    pairs = list(zip(versions, dataset_IDs))
    sorted_pairs = sorted(pairs, key=lambda x:x[0])
    sorted_version, sorted_dataset_ID = zip(*sorted_pairs)

    return list(sorted_dataset_ID)

def retrieveDatasetDetails(dataset_details):
    """
    Take out the dataset version only

    Args:
        dataset_details (Dataset object): stores the Dataset object retrieved from ClearML

    Returns:
        Dictionary: For each Dataset ID, retrieve the version of the dataset.
    """
    dataset_details_dict = {}
    for key, val in dataset_details.items():
        warning(f"")
        warning(f"")
        warning(f"values: {val.__dict__}")
        warning(f"")
        warning(f"")
        dataset_details_dict[key] = {
            "project": val.project,
            "name": val.name,
            "version": val._dataset_version,
            "description": val._task.comment
        }
    return dataset_details_dict

def renderVersionTree():
    """
    Retrieve specified dataset's objects from ClearML, 
    and return the values through render_template to display on the frontend.

    Returns:
        render_template: 
            Returns the dictionary that stores the dependency graph,
            the list of IDs available from the specified dataset,
            and the details of the dataset tagged to its own ID in a dictionary. I parsed through and retrieved only the dataset version
    """
    palkia_dependency_graph = None
    dataset_IDs = []
    dataset_details = {}
    retrieved_dataset = getDataset()
    palkia_dependency_graph = getDependencyGraph(retrieved_dataset)
    
    for key, val in palkia_dependency_graph.items():
        dataset_details[key] = getAllDatasetID(key)
        dataset_IDs.append(key)

    dataset_IDs = sortDataset(dataset_IDs, dataset_details)
    warning(f"CHECKING DATASET ID AND DETAILS:")
    warning(f"{dataset_IDs}")

    dataset_details = retrieveDatasetDetails(dataset_details)
    # try:
    #     for each_id in dataset_IDs:
    #         dataset_details[each_id] = Dataset.get(
    #             dataset_id=each_id,
    #         )
    #         warning(f"GETTING DATASET FOR ID {each_id} SUCCESS")
    # except Exception as e:
    #     warning(f"FAILED TO RETRIEVE DATASET OBJECTS FOR EACH DATASET. ERROR: {e}")
    return render_template(
        'versionTree.html', 
        palkia_dependency_graph=palkia_dependency_graph, 
        dataset_IDs=dataset_IDs, 
        dataset_details=dataset_details
    )



class VersiontreePlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IBlueprint)

    # IConfigurer
    def update_config(self, config_):
        toolkit.add_template_directory(config_, "templates")
        toolkit.add_public_directory(config_, "public")
        toolkit.add_resource("assets", "versiontree")

    # IBlueprint
    def get_blueprint(self):
        blueprint = Blueprint(self.name, self.__module__)
        blueprint.template_folder = 'templates'

        rules = [
            ('/versiontree', 'versiontree', renderVersionTree),
        ]

        for rule in rules:
            blueprint.add_url_rule(*rule)
        
        return blueprint