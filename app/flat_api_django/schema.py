import graphene

import charges.schema


class Query(charges.schema.Query, graphene.ObjectType):
    # This class will inherit from multiple Queries
    # as we begin to add more apps to our project
    pass

class Mutations(graphene.ObjectType):
    delete_charge = charges.schema.DeleteCharge.Field()

schema = graphene.Schema(query=Query, mutation=Mutations)
