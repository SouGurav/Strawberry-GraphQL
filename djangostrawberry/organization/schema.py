import strawberry
from .models import Organization, Employee
from django.db.models import Q

@strawberry.django.type(Organization)
class OrganizationType:
    id: int
    name: str
    establish_date: str | None
    ORD_ID: int | None

    #create another field attribute employees
    @strawberry.field 
    def employees(self) -> list["EmployeeType"]:
        return Employee.objects.filter(organization_id=self.id)

    
@strawberry.input
class Organizationinput:
    id: int
    name: str
    establish_date: str | None 
    ORD_ID: int | None

@strawberry.django.type(Employee)
class EmployeeType:
    employee_id: int
    name: str
    joining_date: str
    releiving_date: str | None
    organization: "OrganizationType"


@strawberry.input
class EmployeeInput:
    name: str
    employee_id: int
    joining_date: str
    releiving_date: str | None
    organization_id: int

@strawberry.input
class UpdateEmployeeInput:
    employee_id: int
    # add " = None" to make specific field as optional and set them to None
    name: str | None = None
    joining_date : str | None = None
    releiving_date: str | None = None
    organization_id: int | None = None

@strawberry.type
class Query:
    organizations: list[OrganizationType] = strawberry.django.field()
    employees: list[EmployeeType] = strawberry.django.field()

    @strawberry.field
    def get_organization_by_id(id: int) -> OrganizationType:
        return Organization.objects.get(ORD_ID=id)

    @strawberry.field
    def get_employee_by_id(employee_id: int) -> EmployeeType:
        return Employee.objects.get(employee_id=employee_id)
    
    @strawberry.field
    def filtered_employees(self,organization_id: int | None = None,joining_date_after: str | None = None,
        joining_date_before: str | None = None) -> list[EmployeeType]:
        filters = {} #define empty dictionary
        if organization_id:
            filters["organization_id"] = organization_id
        if joining_date_after:
            filters["joining_date__gte"] = joining_date_after
        if joining_date_before:
            filters["joining_date__lte"] = joining_date_before

        return Employee.objects.filter(**filters) #pass paramters as dictionary
    

  


@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_employee(self, input: EmployeeInput) -> EmployeeType:
        organization = Organization.objects.get(pk=input.organization_id)
        employee = Employee.objects.create(
            name=input.name,
            employee_id=input.employee_id,
            joining_date=input.joining_date,
            releiving_date=input.releiving_date,
            organization=organization,
        )
        return employee
    
    @strawberry.mutation
    def create_organization(self,input:Organizationinput)-> OrganizationType:
        org = Organization.objects.create(
            id = input.id,
            name = input.name,
            establish_date = input.establish_date,
            ORD_ID = input.ORD_ID,
        )
        return org
    @strawberry.mutation
    def update_employee(self, input: UpdateEmployeeInput) -> EmployeeType:
        try:
            employee = Employee.objects.get(employee_id=input.employee_id)
            if input.name:
                employee.name = input.name
            if input.joining_date:
                employee.joining_date = input.joining_date
            if input.releiving_date:
                employee.releiving_date = input.releiving_date
            if input.organization_id:
                organization = Organization.objects.get(pk=input.organization_id)
                employee.organization = organization
            employee.save()
            return employee
        except Employee.DoesNotExist:
            raise Exception(f"Employee with ID {input.employee_id} not found.")
    
    @strawberry.mutation
    def delete_employee(self, employee_id: int) -> str:
        try:
            employee = Employee.objects.get(employee_id=employee_id)
            employee.delete()
            return f"Employee with ID {employee_id} has been deleted."
        except Employee.DoesNotExist:
            raise Exception(f"Employee with ID {employee_id} not found.")

schema = strawberry.Schema(query=Query, mutation=Mutation)
