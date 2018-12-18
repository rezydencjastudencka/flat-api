import graphene
from django.contrib.auth.models import User

from django.db import transaction
from graphene_django.types import DjangoObjectType

from charges.models import Flat, Profile, Charge
from session.decorators import none_if_unauthenticated, raise_if_unauthenticated
from transfers.models import Transfer


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


class TransferType(DjangoObjectType):
    class Meta:
        model = Transfer


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


class ChargeSummaryType(graphene.ObjectType):
    user = graphene.Field(UserType)
    amount = graphene.Float()

    def resolve_user(self, info, **kwargs):
        return self['user']

    def resolve_amount(self, info, **kwargs):
        return self['amount']


class SummaryType(graphene.ObjectType):
    monthly = graphene.List(ChargeSummaryType,
                            year=graphene.Int(required=True),
                            month=graphene.Int(required=True))

    def resolve_monthly(self, info, **kwargs):
        year = kwargs.get('year')
        month = kwargs.get('month')

        summary = Charge.get_summary_new(year, month, info.context.user)
        return summary.values()


class Query(object):
    expenses = graphene.List(ExpenseType,
                             year=graphene.Int(required=True),
                             month=graphene.Int(required=True))
    expense = graphene.Field(ExpenseType,
                             id=graphene.ID(required=True))
    revenues = graphene.List(RevenueType,
                             year=graphene.Int(required=True),
                             month=graphene.Int(required=True))
    revenue = graphene.Field(RevenueType,
                             id=graphene.ID(required=True))
    transfers = graphene.List(TransferType,
                              year=graphene.Int(required=True),
                              month=graphene.Int(required=True))
    me = graphene.Field(UserType)

    users = graphene.List(UserType)

    summary = graphene.Field(SummaryType)

    @raise_if_unauthenticated
    def resolve_expenses(self, info, **kwargs):
        year = kwargs.get('year')
        month = kwargs.get('month')

        return Charge.get_expenses(year, month, info.context.user)

    @raise_if_unauthenticated
    def resolve_expense(self, info, id, **kwargs):
        return Charge.get_expense(id, info.context.user)

    @raise_if_unauthenticated
    def resolve_revenues(self, info, **kwargs):
        year = kwargs.get('year')
        month = kwargs.get('month')

        return Charge.get_revenues(year, month, info.context.user)

    @raise_if_unauthenticated
    def resolve_revenue(self, info, id, **kwargs):
        return Charge.get_revenue(id, info.context.user)

    @raise_if_unauthenticated
    def resolve_transfers(self, info, **kwargs):
        year = kwargs.get('year')
        month = kwargs.get('month')

        return Transfer.get_user_transfers(year, month, info.context.user)

    @raise_if_unauthenticated
    def resolve_me(self, info, **kwargs):
        return info.context.user

    @raise_if_unauthenticated
    def resolve_users(self, info, **kwargs):
        return User.objects.filter(profile__flat=info.context.user.profile.flat)

    @raise_if_unauthenticated
    def resolve_summary(self, info):
        return SummaryType()


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


class AddTransfer(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        amount = graphene.Float(required=True)
        date = graphene.types.datetime.Date(required=True)
        to = graphene.NonNull(graphene.ID)

    Output = TransferType

    @raise_if_unauthenticated
    def mutate(self, info, name, amount, date, to):
        transfer = Transfer(from_user=info.context.user,
                            to_user=User.objects.get(pk=to),
                            amount=amount, name=name,
                            date=date)
        transfer.save()

        return transfer


class DeleteTransfer(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    status = graphene.Field(StatusCodes, required=True)

    @raise_if_unauthenticated
    def mutate(self, info, id):
        deletedObjs, _ = Transfer.objects.filter(
            from_user=info.context.user,
            id=id
        ).delete()
        if deletedObjs >= 1:
            status = StatusCodes.SUCCESS.value
        else:
            status = StatusCodes.NOT_FOUND.value

        return DeleteTransfer(status=status)


class Mutation(object):
    add_revenue = AddRevenue.Field()
    create_flat = CreateFlat.Field()
    join_flat = JoinFlat.Field()
    delete_revenue = DeleteRevenue.Field()
    add_transfer = AddTransfer.Field()
    delete_transfer = DeleteTransfer.Field()
