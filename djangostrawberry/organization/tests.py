from django.test import TestCase, Client
from django.contrib.auth.models import User
import jwt
from datetime import datetime, timedelta
from .models import Organization, Employee
from .views import generate_jwt, decode_jwt  # Ensure you have these methods

class GraphQLTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='1234')
        self.token = generate_jwt(self.user)

    def test_login(self):
        response = self.client.post('/graphql/', {
            'query': '''
            mutation {
                login(username: "testuser", password: "1234") {
                    token
                    username
                }
            }
            '''
        }, content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.json()['data']['login'])

    def test_create_organization(self):
        response = self.client.post('/graphql/', {
            'query': '''
            mutation {
                createOrganization(input: { id: 1, name: "New Org", establishDate: "2022-01-01", ORDId: 1 }) {
                    id
                    name
                }
            }
            '''
        }, HTTP_AUTHORIZATION=f'Bearer {self.token}', content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('id', response.json()['data']['createOrganization'])

    def test_create_employee(self):
        Organization.objects.create(id=1, name="New Org", establish_date="2022-01-01", ORD_ID=1)
        response = self.client.post('/graphql/', {
            'query': '''
            mutation {
                createEmployee(input: { name: "John Doe", employeeId: 123, joiningDate: "2022-01-01", releivingDate: null, organizationId: 1 }) {
                    employeeId
                    name
                }
            }
            '''
        }, HTTP_AUTHORIZATION=f'Bearer {self.token}', content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('employeeId', response.json()['data']['createEmployee'])

    def test_get_organization_by_id(self):
        Organization.objects.create(id=1, name="New Org", establish_date="2022-01-01", ORD_ID=1)
        response = self.client.post('/graphql/', {
            'query': '''
            query {
                getOrganizationById(id: 1) {
                    id
                    name
                }
            }
            '''
        }, HTTP_AUTHORIZATION=f'Bearer {self.token}', content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('getOrganizationById', response.json()['data'])

    def test_get_employee_by_id(self):
        org = Organization.objects.create(id=1, name="New Org", establish_date="2022-01-01", ORD_ID=1)
        Employee.objects.create(employee_id=123, name="John Doe", joining_date="2022-01-01", organization=org)
        response = self.client.post('/graphql/', {
            'query': '''
            query {
                getEmployeeById(employeeId: 123) {
                    employeeId
                    name
                }
            }
            '''
        }, HTTP_AUTHORIZATION=f'Bearer {self.token}', content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('getEmployeeById', response.json()['data'])
    
    def test_update_employee(self): 
        org = Organization.objects.create(id=1, name="New Org", establish_date="2022-01-01", ORD_ID=1) 
        Employee.objects.create(employee_id=123, name="John Doe", joining_date="2022-01-01", organization=org) 
        response = self.client.post('/graphql/', { 'query': ''' mutation { updateEmployee(input: 
                                                  { employeeId: 123, name: "Jane Doe" }) { employeeId name } } ''' }, 
                                                  HTTP_AUTHORIZATION=f'Bearer {self.token}', content_type='application/json') 
        self.assertEqual(response.status_code, 200) 
        self.assertEqual(response.json()['data']['updateEmployee']['name'], "Jane Doe")



    def test_delete_employee(self):
        org = Organization.objects.create(id=1, name="New Org", establish_date="2022-01-01", ORD_ID=1)
        Employee.objects.create(employee_id=123, name="John Doe", joining_date="2022-01-01", organization=org)
        response = self.client.post('/graphql/', {
            'query': '''
            mutation {
                deleteEmployee(employeeId: 123)
            }
            '''
        }, HTTP_AUTHORIZATION=f'Bearer {self.token}', content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('Employee with ID 123 has been deleted.', response.json()['data']['deleteEmployee'])

    def test_filtered_employees(self):
        organization = Organization.objects.create(id=1, name="New Org", establish_date="2000-01-01", ORD_ID=1)
        Employee.objects.create(employee_id=101, name="Alice", joining_date="2004-01-05", organization=organization) 
        Employee.objects.create(employee_id=102, name="Bob", joining_date="2022-02-10", organization=organization) 
        Employee.objects.create(employee_id=103, name="Charlie", joining_date="2003-03-15", organization=organization) 
        response = self.client.post('/graphql/', { 'query': ''' query 
                                                  { filteredEmployees(organizationId: 1, 
                                                  joiningDateAfter: "2003-01-01", 
                                                  joiningDateBefore: "2022-02-28") 
                                                  { employeeId name } } ''' }, 
                                                  HTTP_AUTHORIZATION=f'Bearer {self.token}', 
                                                  content_type='application/json') 
        self.assertEqual(response.status_code, 200) 
        filtered_employees = response.json()['data']['filteredEmployees'] 
        self.assertEqual(len(filtered_employees), 3) 
        self.assertEqual(filtered_employees[0]['name'], "Alice") 
        self.assertEqual(filtered_employees[1]['name'], "Bob")
        print("All test  cases passed")
