
"""
    eve_mongoengine.datalayer
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    This module implements eve's data layer which uses mongoengine models
    instead of direct pymongo access.

    :copyright: (c) 2014 by Stanislav Heller.
    :license: BSD, see LICENSE for more details.
"""

# builtin
import sys
import ast
import json
from uuid import UUID
import traceback

# 3rd party
from werkzeug.exceptions import HTTPException
from flask import abort
import pymongo
from mongoengine import (DoesNotExist, EmbeddedDocumentField, DictField,
                         MapField, ListField, FileField)
from mongoengine.connection import get_db, connect

# eve
from eve.io.mongo import Mongo, MongoJSONEncoder
from eve.io.mongo.parser import parse, ParseError
from eve.utils import (
    config, debug_error_message, validate_filters, document_etag
)
from eve.exceptions import ConfigException

# Python3 compatibility
from ._compat import itervalues, iteritems


def _itemize(maybe_dict):
    if isinstance(maybe_dict, list):
        return maybe_dict
    elif isinstance(maybe_dict, dict):
        return iteritems(maybe_dict)
    else:
        raise TypeError("Wrong type to itemize. Allowed lists and dicts.")


class PymongoQuerySet(object):
    """
    Dummy mongoenigne-like QuerySet behaving just like queryset
    with as_pymongo() called, but returning ALL fields in subdocuments
    (which as_pymongo() somehow filters).
    """
    def __init__(self, qs):
        self._qs = qs

    def __iter__(self):
        def iterate(obj):
            qs = object.__getattribute__(obj, '_qs')
            for doc in qs:
                doc = dict(doc.to_mongo())
                for attr, value in iteritems(dict(doc)):
                    if isinstance(value, (list, dict)) and not value:
                        del doc[attr]
                yield doc
        return iterate(self)

    def __getattribute__(self, name):
        return getattr(object.__getattribute__(self, '_qs'), name)


class MongoengineJsonEncoder(MongoJSONEncoder):
    """
    Propretary JSON encoder to support special mongoengine's special fields.
    """
    def default(self, obj):
        if isinstance(obj, UUID):
            # rendered as a string
            return str(obj)
        else:
            # delegate rendering to base class method
            return super(MongoengineJsonEncoder, self).default(obj)


class MongoengineDataLayer(Mongo):
    """
    Data layer for eve-mongoengine extension.

    Most of functionality is copied from :class:`eve.io.mongo.Mongo`.
    """
    #: default JSON encoder
    json_encoder_class = MongoengineJsonEncoder

    #: list of mongoengine field types, which consist of another fields
    _structured_fields = (EmbeddedDocumentField, DictField, MapField)

    #: name of default queryset, where datalayer asks for data
    default_queryset = 'objects'

    #: Options for usage of mongoengine layer.
    #: use_atomic_update_for_patch - when set to True, Mongoengine layer will
    #: use update_one() method (which is atomic) for updating. But then you
    #: will loose your pre/post-save hooks. When you set this to False, for
    #: updating will be used save() method.
    mongoengine_options = {
        'use_atomic_update_for_patch': True
    }

    def __init__(self, ext):
        """
        Constructor.

        :param ext: instance of :class:`EveMongoengine`.
        """
        # get authentication info
        username = ext.app.config['MONGO_USERNAME']
        password = ext.app.config['MONGO_PASSWORD']
        auth = (username, password)
        if any(auth) and not all(auth):
            raise ConfigException('Must set both USERNAME and PASSWORD '
                                  'or neither')
        # try to connect to db
        self.conn = connect(ext.app.config['MONGO_DBNAME'],
                            host=ext.app.config['MONGO_HOST'],
                            port=ext.app.config['MONGO_PORT'])
        self.models = ext.models
        self.app = ext.app
        # create dummy driver instead of PyMongo, which causes errors
        # when instantiating after config was initialized
        self.driver = type('Driver', (), {})()
        self.driver.db = get_db()
        # authenticate
        if any(auth):
            self.driver.db.authenticate(username, password)
        # FIX wrongly generated etags because of empty lists
        self._install_etag_fixer()

    def _install_etag_fixer(self):
        """
        Fixes ETag value returned by PATCH responses.
        """
        self._etag_doc = None

        def fix_patch_etag(resource, request, payload):
            if self._etag_doc is None:
                return
            # make doc from which the etag will be computed
            etag_doc = self._clean_doc(self._etag_doc)
            # load the response back agagin from json
            d = json.loads(payload.get_data(as_text=True))
            # compute new etag
            d[config.ETAG] = document_etag(etag_doc)
            payload.set_data(json.dumps(d))

        self.app.on_post_PATCH += fix_patch_etag

    def _handle_exception(self, exc):
        """
        If application is in debug mode, prints every traceback to stderr.
        """
        if self.app.debug:
            traceback.print_exc(file=sys.stderr)
        raise exc

    def _structure_in_model(self, model_cls):
        """
        Returns True if model contains some kind of structured field.
        """
        for field in itervalues(model_cls._fields):
            if isinstance(field, self._structured_fields):
                return True
            elif isinstance(field, ListField):
                if isinstance(field.field, self._structured_fields):
                    return True
        return False

    def _projection(self, resource, projection, qry):
        """
        Ensures correct projection for mongoengine query.
        """
        if projection is None:
            return qry

        projection_value = set(projection.values())
        projection = set(projection.keys())

        # strip special underscore prefixed attributes -> in mongoengine
        # they arent prefixed
        model_cls = self._get_model_cls(resource)
        projection.discard('_id')
        rev_map = model_cls._reverse_db_field_map
        projection = [rev_map[field] for field in projection]
        if 0 in projection_value:
            qry = qry.exclude(*projection)
        else:
            # id has to be always there
            projection.append('id')
            qry = qry.only(*projection)
        return qry

    def _get_model_cls(self, resource):
        try:
            return self.models[resource]
        except KeyError:
            abort(404)

    def _objects(self, resource):
        _cls = self._get_model_cls(resource)
        try:
            return getattr(_cls, self.default_queryset)
        except AttributeError:
            # falls back to default `objects` QuerySet
            return _cls.objects

    def find(self, resource, req, sub_resource_lookup):
        """
        Seach for results and return list of them.

        :param resource: name of requested resource as string.
        :param req: instance of :class:`eve.utils.ParsedRequest`.
        :param sub_resource_lookup: sub-resource lookup from the endpoint url.
        """
        qry = self._objects(resource)

        client_projection = {}
        client_sort = {}
        spec = {}

        # TODO sort syntax should probably be coherent with 'where': either
        # mongo-like # or python-like. Currently accepts only mongo-like sort
        # syntax.

        # TODO should validate on unknown sort fields (mongo driver doesn't
        # return an error)
        if req.sort:
            try:
                client_sort = ast.literal_eval(req.sort)
            except Exception as e:
                abort(400, description=debug_error_message(str(e)))

        if req.where:
            try:
                spec = self._sanitize(json.loads(req.where))
            except HTTPException as e:
                # _sanitize() is raising an HTTP exception; let it fire.
                raise
            except:
                try:
                    spec = parse(req.where)
                except ParseError:
                    abort(400, description=debug_error_message(
                        'Unable to parse `where` clause'
                    ))

        if sub_resource_lookup:
            spec.update(sub_resource_lookup)

        spec = self._mongotize(spec, resource)

        bad_filter = validate_filters(spec, resource)
        if bad_filter:
            abort(400, bad_filter)

        client_projection = self._client_projection(req)

        datasource, spec, projection, sort = self._datasource_ex(
            resource,
            spec,
            client_projection,
            client_sort)
        # apply ordering
        if sort:
            for field, direction in _itemize(sort):
                if direction < 0:
                    field = "-%s" % field
                qry = qry.order_by(field)
        # apply filters
        if req.if_modified_since:
            spec[config.LAST_UPDATED] = \
                {'$gt': req.if_modified_since}
        if len(spec) > 0:
            qry = qry.filter(__raw__=spec)
        # apply projection
        qry = self._projection(resource, projection, qry)
        # apply limits
        if req.max_results:
            qry = qry.limit(req.max_results)
        if req.page > 1:
            qry = qry.skip((req.page - 1) * req.max_results)
        return PymongoQuerySet(qry)

    def find_one(self, resource, req, **lookup):
        """
        Look for one object.
        """
        # transform every field value to correct type for querying
        lookup = self._mongotize(lookup, resource)

        client_projection = self._client_projection(req)
        datasource, filter_, projection, _ = self._datasource_ex(
            resource,
            lookup,
            client_projection)
        qry = self._objects(resource)

        if len(filter_) > 0:
            qry = qry.filter(__raw__=filter_)

        qry = self._projection(resource, projection, qry)
        try:
            doc = dict(qry.get().to_mongo())
            return self._clean_doc(doc)
        except DoesNotExist:
            return None

    def _doc_to_model(self, resource, doc):
        if '_id' in doc:
            doc['id'] = doc.pop('_id')
        cls = self._get_model_cls(resource)
        instance = cls(**doc)
        for attr, field in iteritems(cls._fields):
            # Inject GridFSProxy object into the instance for every FileField.
            # This is because the Eve's GridFS layer does not work with the
            # model object, but handles insertion in his own workspace. Sadly,
            # there's no way how to work around this, so we need to do this
            # special hack..
            if isinstance(field, FileField):
                if attr in doc:
                    proxy = field.get_proxy_obj(key=field.name,
                                                instance=instance)
                    proxy.grid_id = doc[attr]
                    instance._data[attr] = proxy
        return instance

    def _clean_doc(self, doc):
        """Cleans empty datastructured to get proper etag"""
        for attr, value in iteritems(dict(doc)):
            if isinstance(value, (list, dict)) and not value:
                del doc[attr]
        return doc

    def insert(self, resource, doc_or_docs):
        """Called when performing POST request"""
        datasource, filter_, _, _ = self._datasource_ex(resource)
        try:
            if isinstance(doc_or_docs, list):
                ids = []
                for doc in doc_or_docs:
                    model = self._doc_to_model(resource, doc)
                    model.save(write_concern=self._wc(resource))
                    ids.append(model.id)
                    doc.update(dict(model.to_mongo()))
                    doc[config.ID_FIELD] = model.id
                    self._clean_doc(doc)
                return ids
            else:
                model = self._doc_to_model(resource, doc_or_docs)
                model.save(write_concern=self._wc(resource))
                doc_or_docs.update(dict(model.to_mongo()))
                doc_or_docs[config.ID_FIELD] = model.id
                self._clean_doc(doc_or_docs)
                return model.id
        except pymongo.errors.OperationFailure as e:
            # most likely a 'w' (write_concern) setting which needs an
            # existing ReplicaSet which doesn't exist. Please note that the
            # update will actually succeed (a new ETag will be needed).
            abort(500, description=debug_error_message(
                'pymongo.errors.OperationFailure: %s' % e
            ))
        except Exception as exc:
            self._handle_exception(exc)

    def _transform_updates_to_mongoengine_kwargs(self, resource, updates):
        """
        Transforms update dict to special mongoengine syntax with set__,
        unset__ etc.
        """
        field_cls = self._get_model_cls(resource)
        nopfx = lambda x: field_cls._reverse_db_field_map[x]
        return dict(("set__%s" % nopfx(k), v) for (k, v) in iteritems(updates))

    def _has_empty_list_recurse(self, value):
        if value == []:
            return True
        if isinstance(value, dict):
            return self._has_empty_list(value)
        elif isinstance(value, list):
            for val in value:
                if self._has_empty_list_recurse(val):
                    return True
        return False

    def _has_empty_list(self, updates):
        """
        Traverses updates and returns True if there is update to empty list.
        """
        for key, value in iteritems(updates):
            if self._has_empty_list_recurse(value):
                return True
        return False

    def _update_using_update_one(self, resource, id_, updates):
        """
        Updates one document atomically using QuerySet.update_one().
        """
        kwargs = self._transform_updates_to_mongoengine_kwargs(resource,
                                                               updates)
        qry = self._objects(resource)(id=id_)
        qry.update_one(write_concern=self._wc(resource), **kwargs)
        if self._has_empty_list(updates):
            # Fix Etag when updating to empty list
            model = self._objects(resource)(id=id_).get()
            self._etag_doc = dict(model.to_mongo())
        else:
            self._etag_doc = None

    def _update_document(self, doc, updates):
        """
        Makes appropriate calls to update mongoengine document properly by
        update definition given from REST API.
        """
        for db_field, value in iteritems(updates):
            field_name = doc._reverse_db_field_map[db_field]
            field = doc._fields[field_name]
            doc[field_name] = field.to_python(value)
        return doc

    def _update_using_save(self, resource, id_, updates):
        """
        Updates one document non-atomically using Document.save().
        """
        model = self._objects(resource)(id=id_).get()
        self._update_document(model, updates)
        model.save(write_concern=self._wc(resource))
        # Fix Etag when updating to empty list
        self._etag_doc = dict(model.to_mongo())

    def update(self, resource, id_, updates):
        """Called when performing PATCH request."""
        try:
            if self.mongoengine_options.get('use_atomic_update_for_patch', 1):
                self._update_using_update_one(resource, id_, updates)
            else:
                self._update_using_save(resource, id_, updates)
        except pymongo.errors.OperationFailure as e:
            # see comment in :func:`insert()`.
            abort(500, description=debug_error_message(
                'pymongo.errors.OperationFailure: %s' % e
            ))
        except Exception as exc:
            self._handle_exception(exc)

    def replace(self, resource, id_, document):
        """Called when performing PUT request."""
        try:
            # FIXME: filters?
            model = self._doc_to_model(resource, document)
            model.save(write_concern=self._wc(resource))
        except pymongo.errors.OperationFailure as e:
            # see comment in :func:`insert()`.
            abort(500, description=debug_error_message(
                'pymongo.errors.OperationFailure: %s' % e
            ))
        except Exception as exc:
            self._handle_exception(exc)

    def remove(self, resource, lookup):
        """Called when performing DELETE request."""
        lookup = self._mongotize(lookup, resource)
        datasource, filter_, _, _ = self._datasource_ex(resource, lookup)

        try:
            if not filter_:
                qry = self._objects(resource)
            else:
                qry = self._objects(resource)(__raw__=filter_)
            qry.delete(write_concern=self._wc(resource))
        except pymongo.errors.OperationFailure as e:
            # see comment in :func:`insert()`.
            abort(500, description=debug_error_message(
                'pymongo.errors.OperationFailure: %s' % e
            ))
        except Exception as exc:
            self._handle_exception(exc)