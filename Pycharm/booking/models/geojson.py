import json
from services import log
import os.path

logger = log.get_logger('geojson.py')


class Feature:
    def __init__(self, id, geometry, properties, data):
        self.type = "Feature"
        self.id = id
        self.geometry = geometry
        self.properties = properties
        self.data = data

    def json(self):
        return json.dumps({
            "type": self.type,
            "id": self.id,
            "geometry": self.geometry,
            "properties": self.properties,
            "data": self.data
        })

    def dict(self):
        return {
            "type": self.type,
            "id": self.id,
            "geometry": self.geometry,
            "properties": self.properties,
            "data": self.data
        }


class FeatureCollection:
    def __init__(self):
        self.type = "FeatureCollection"
        self.features = []

    def add_feature(self, feature: Feature):
        if feature:
            # turn Feature object json format (type string) into a dict
            feature_dict = json.loads(feature.json())
            # validate Feature required keys according to geojson RFC
            if feature_dict['type'] == "Feature" and all(k in feature_dict for k in ("geometry", "id", "properties")):
                self.features.append(feature_dict)
                logger.info('added ' + str(feature.id) + ' successfully')
                # print('added ' + str(feature.id) + ' successfully')
        else:
            logger.warning('feature not added')
            # print('feature not added')

    def extend_features(self, features):
        self.features.extend(features)

    def json(self):
        return json.dumps({
            "type": self.type,
            "features": self.features
        })


class GeoJsonFileHandler:
    def get_collection_ids(self, file_path):
        collection_ids = []
        if os.path.exists(file_path):
            with open(file_path) as geojson_file:
                feature_collection = json.load(geojson_file)
                collection_ids = [str(feature['id']) for feature in feature_collection['features']]
        return collection_ids

    def get_collection_features(self, file_path):
        features = []
        if os.path.exists(file_path):
            with open(file_path) as geojson_file:
                feature_collection = json.load(geojson_file)
                features = feature_collection['features']
        return features
