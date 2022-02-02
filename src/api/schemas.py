from marshmallow import fields, Schema
from marshmallow.validate import Length, Range


class DatasetQuerySchema(Schema):
    k_folds = fields.Integer(strict=False, required=False, data_key='kFolds', validate=Range(min=1))
    test_split = fields.Float(strict=True, required=False, data_key='testSplit',
                              validate=Range(min=0.0, max=1.0, min_inclusive=False, max_inclusive=False))
    validation_split = fields.Float(strict=True, required=False, data_key='validationSplit',
                                    validate=Range(min=0.0, max=1.0, min_inclusive=False, max_inclusive=False))
    seed = fields.String(strict=False, required=False, data_key='seed')


class MappingSchema(Schema):
    name = fields.String(required=True, validate=Length(min=1))
    description = fields.String(required=False, load_default='')
    aliases = fields.List(fields.String(), required=False, load_default=list)
    tasks = fields.List(fields.String(), required=False, load_default=list)


class DatasetCreationSchema(Schema):
    name = fields.String(required=True, validate=Length(min=1))
    description = fields.String(required=False, load_default='')
    train_data = fields.List(fields.URL(), required=True, data_key='trainDocuments')
    test_data = fields.List(fields.URL(), required=False, data_key='testDocuments', load_default=list)
    mappings = fields.List(fields.Nested(MappingSchema), required=False, load_default=list)


class DatasetPatchSchema(Schema):
    id = fields.String(required=True, validate=Length(min=1))
    name = fields.String(required=False, validate=Length(min=1))
    description = fields.String(required=False)
    train_data = fields.List(fields.URL(), required=False, data_key='trainDocuments')
    test_data = fields.List(fields.URL(), required=False, data_key='testDocuments')
    mappings = fields.List(fields.Nested(MappingSchema), required=False)
