from pydantic import BaseModel
from pydantic.alias_generators import to_camel


class ViewModel(BaseModel):
    model_config = {
        "alias_generator": to_camel,  # snake → camel
        "populate_by_name": True,  # accepts snake_case inputs
        "from_attributes": True,  # permits reading attributes
    }
