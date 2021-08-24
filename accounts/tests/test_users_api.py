from accounts.models import Doctor, Patient
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('accounts:create')
CREATE_TOKEN_URL = reverse('accounts:token')
USER_PROFILE_PAGE = reverse('accounts:me')


def create_user(**kwargs):
    return get_user_model().objects.create_user(**kwargs)


class PublicUserApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_create_valid_patient_user_success(self):
        """Test creating user with a valid payload 
            i.e valid email, pass, username
        """
        payload = {
            'email': 'k@gmail.com',
            'password': 'testTSET1230',
            'name': "khaled osman",
            'user_type': 'patient'
        }

        res = self.client.post(CREATE_USER_URL, payload)

        # check results
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        # test patient exits
        patient_exists = Patient.objects.filter(user=user).exists()
        doctor_exists = Doctor.objects.filter(user=user).exists()
        self.assertTrue(patient_exists)
        self.assertFalse(doctor_exists)

        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)
        
    def test_create_valid_doctor_user_success(self):
        """Test creating user with a valid payload 
            i.e valid email, pass, username
        """
        payload = {
            'email': 'k@gmail.com',
            'password': 'testTSET1230',
            'name': "khaled osman",
            'user_type': 'doctor'
        }

        res = self.client.post(CREATE_USER_URL, payload)

        # check results
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        # test doctor exits
        doctor_exists = Doctor.objects.filter(user=user).exists()
        patient_exists = Patient.objects.filter(user=user).exists()
        self.assertTrue(doctor_exists)
        self.assertFalse(patient_exists)

        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)
        

    def test_create_an_existing_user(self):
        """ this test must fail """
        payload = {
            'email': 'k@gmail.com',
            'password': 'testTSET1230',
            'name': "khaled osman"
        }

        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        

    def test_password_too_short(self):
        """Test that the password must be more than 5 characters"""
        payload = {
            'email': 'k@gmail.com',
            'password': 'te0',
            'name': "khaled osman"
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        # make sure app does not create this user
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()

        self.assertFalse(user_exists)
        

    def test_create_token_for_valid_user(self):
        """ create auth tokens for valid users  """
        payload = {
            'email': 'k@gmail.com',
            'password': 'pass1232321PASS',
            'name': "khaled osman"
        }
        create_user(**payload)
        res = self.client.post(CREATE_TOKEN_URL, payload)
        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        

    def test_create_token_for_invalid_credentails(self):
        """ create auth tokens for valid users  """
        payload = {
            'email': 'k@gmail.com',
            'password': 'pass1232321PASS',
            'name': "khaled osman"
        }
        create_user(**payload)
        payload['password'] = "wrong pass"
        res = self.client.post(CREATE_TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        

    def test_create_token_for_non_existing_user(self):
        """ create auth tokens for valid users  """
        payload = {
            'email': 'k@gmail.com',
            'password': 'pass1232321PASS',
            'name': "khaled osman"
        }
        res = self.client.post(CREATE_TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        

    def test_create_token_for_missing_user_fields(self):
        """ create auth tokens for valid users  """
        payload = {
            'email': 'k@gmail.com',
            'password': 'pass1232321PASS',
            'name': "khaled osman"
        }
        create_user(**payload)
        payload['password'] = ''
        res = self.client.post(CREATE_TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
       

    def test_retreive_user_unauthorized(self):
        """ Test that auth is required to acces user profile """
        res = self.client.get(USER_PROFILE_PAGE)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
       


class PrivateUserApiTest(TestCase):
    """Test API requests that require authentication like login , update user data"""

    def setUp(self):
        self.user = create_user(
            email='k@gmail.com',
            password='pass1232321PASS',
            name="khaled osman"
        )

        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_post_to_profile_page_not_allowd(self):
        """ the allowd method are only put and patch """
        res = self.client.post(USER_PROFILE_PAGE, {})
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile_authenticated_only(self):
        """Test updating the user profile for authenticated user"""
        payload = {'name': 'new name', 'password': 'newpassword123'}
        res = self.client.patch(USER_PROFILE_PAGE, payload)
        # get new updated user from the db
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
