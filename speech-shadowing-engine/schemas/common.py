from bson import ObjectId
from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema


class PyObjectId(ObjectId):

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type,
        handler: GetCoreSchemaHandler,
    ):
        return core_schema.json_or_python_schema(
            json_schema=core_schema.str_schema(),
            python_schema=core_schema.no_info_plain_validator_function(cls.validate),
        )

    @classmethod
    def validate(cls, value):
        if isinstance(value, ObjectId):
            return value
        if not ObjectId.is_valid(value):
            raise ValueError("Invalid ObjectId")
        return ObjectId(value)
