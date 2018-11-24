from graphene_django.views import GraphQLView

from flat_api_django.exceptions import UnauthorizedError


class FlatGraphQLView(GraphQLView):

    @staticmethod
    def format_error(error):
        if hasattr(error, 'original_error') and error.original_error:
            formatted = {"message": str(error.original_error)}
            if isinstance(error.original_error, UnauthorizedError):
                formatted['code'] = 401
            return formatted

        return GraphQLView.format_error(error)
