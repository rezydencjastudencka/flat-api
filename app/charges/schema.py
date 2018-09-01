import graphene
from django.contrib.auth.models import User

from django.db import transaction
from graphene_django.types import DjangoObjectType

from charges.models import Flat, Profile
from session.decorators import empty_if_unauthenticated, none_if_unauthenticated, raise_if_unauthenticated
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


class FlatType(DjangoObjectType):
    class Meta:
        model = Flat


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

    @empty_if_unauthenticated
    def resolve_users(self, info, **kwargs):
        return User.objects.filter(profile__flat=info.context.user.profile.flat)


class CreateFlat(graphene.Mutation):
    class Arguments:
        flatname = graphene.String(required=True)
        username = graphene.String(required=True)
        email = graphene.String(required=True)
        password = graphene.String(required=True)

    Output = FlatType

    def mutate(self, info, flatname, username, email, password):
        with transaction.atomic():
            flat = Flat.objects.create(name=flatname)
            user = User.objects.create_user(username, email, password)
            Profile.objects.create(flat=flat, user=user)

            return flat


class JoinFlat(graphene.Mutation):
    class Arguments:
        join_token = graphene.String(required=True)
        username = graphene.String(required=True)
        email = graphene.String(required=True)
        password = graphene.String(required=True)

    Output = FlatType

    def mutate(self, info, join_token, username, email, password):
        with transaction.atomic():
            flat = Flat.objects.filter(join_token__exact=join_token).first()
            user = User.objects.create_user(username, email, password)
            Profile.objects.create(flat=flat, user=user)

            return flat


class AddRevenue(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        amount = graphene.String(required=True)
        date = graphene.types.datetime.Date(required=True)
        to = graphene.List(graphene.NonNull(graphene.ID))

    Output = RevenueType

    @none_if_unauthenticated
    def mutate(self, info, name, amount, date, to):
        with transaction.atomic():
            revenue = Charge(from_user=info.context.user, raw_amount=amount, name=name,
                             date=date)
            revenue.save()

            users = User.objects.filter(id__in=to)
            revenue.to_users.set(users)
            revenue.clean()

        return revenue


class DeleteRevenue(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    status = graphene.Field(StatusCodes, required=True)

    @raise_if_unauthenticated
    def mutate(self, info, id):
        deletedObjs, _ = Charge.objects.filter(
            from_user=info.context.user,
            id=id
        ).delete()
        if deletedObjs > 1:
            status = StatusCodes.SUCCESS.value
        else:
            status = StatusCodes.NOT_FOUND.value

        return DeleteRevenue(status=status)


class Mutation(object):
    add_revenue = AddRevenue.Field()
    create_flat = CreateFlat.Field()
    join_flat = JoinFlat.Field()
    delete_revenue = DeleteRevenue.Field()
