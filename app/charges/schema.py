import graphene
from django.contrib.auth.models import User

from graphene_django.types import DjangoObjectType

from session.decorators import empty_if_unauthenticated
from .models import Charge


class StatusCodes(graphene.Enum):
    NOT_FOUND = 0
    SUCCESS = 1


class ExpenseType(DjangoObjectType):
    amount = graphene.Float()

    def resolve_amount(self, info, **kwargs):
        return self.amount / self.to_users.count()

    class Meta:
        model = Charge
        exclude_fields = ('raw_amount',)


class RevenueType(DjangoObjectType):
    class Meta:
        model = Charge


class UserType(DjangoObjectType):
    class Meta:
        model = User
        only_fields = ('id', 'username')


class Query(object):
    expenses = graphene.List(ExpenseType,
                             year=graphene.Int(required=True),
                             month=graphene.Int(required=True))
    revenues = graphene.List(RevenueType,
                             year=graphene.Int(required=True),
                             month=graphene.Int(required=True))
    users = graphene.List(UserType)

    @empty_if_unauthenticated
    def resolve_expenses(self, info, **kwargs):
        year = kwargs.get('year')
        month = kwargs.get('month')

        return Charge.get_expenses(year, month, info.context.user)

    @empty_if_unauthenticated
    def resolve_revenues(self, info, **kwargs):
        year = kwargs.get('year')
        month = kwargs.get('month')

        return Charge.get_revenues(year, month, info.context.user)

    def resolve_users(self, info, **kwargs):
        return User.objects.none()


class DeleteCharge(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)  # veryfi for id type

    status = graphene.Field(StatusCodes, required=True)

    def mutate(self, info, id):
        deletedObjs,_ = Charge.objects.filter(
            from_user=info.context.user,
            id=id
        ).delete()
        if deletedObjs > 1:
            status = StatusCodes.SUCCESS.value
        else:
            status = StatusCodes.NOT_FOUND.value

        return DeleteCharge(status=status)


class Mutations(object):
    delete_charge = DeleteCharge.Field()
