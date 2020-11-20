"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py

from app import app
import os
from unittest import TestCase

from models import db, User, Recipe, User_Favorite
from sqlalchemy import exc

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///athomecheftest"


# Now we can import app


# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data
db.create_all()


class UserModelTestCase(TestCase):
    """Test user model."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        user1 = User.signup(
            username="user1", 
            first_name = "first1",
            last_name = "last1",
            email="user1@gmail.com", password="password")
        user1.id = 1000
        user1_id = user1.id
    
        db.session.commit()

        self.user1 = User.query.get(user1_id)
        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            first_name= "testfirst",
            last_name="testlast",
            password="HASHED_PASSWORD"
        )
        u.id = 3000
        u_id = u.id
        db.session.add(u)
        db.session.commit()
        user = User.query.get(u_id)

        # User should have no recipes
        self.assertEqual(len(user.recipes), 0)
        self.assertEqual(user.email, "test@test.com")
        self.assertEqual(user.first_name, "testfirst")
        self.assertEqual(user.username, "testuser")



    # def test__repr__(self):
    #     self.assertEqual(self.user1.__repr__(),
    #                      f"<User #{self.user1.id}: {self.user1.username}, {self.user1.email}>")


    def test_valid_signup(self):
        user_test = User.signup(
            "user_test", "testfirst", "testlast", "user_test@gmail.com", "password" )
        user_test.id = 3000
        user_test_id = user_test.id
        db.session.commit()
        test_user = User.query.get(user_test_id)
        self.assertIsNotNone(test_user)
        self.assertEqual(test_user.username, "user_test")
        self.assertEqual(test_user.first_name, "testfirst")
        self.assertEqual(test_user.last_name, "testlast")
        self.assertEqual(test_user.email, "user_test@gmail.com")
        self.assertNotEqual(test_user.password, "password")
        self.assertTrue(test_user.password.startswith("$2b$"))

    def test_invalid_username_signup(self):
        user_test = User.signup(
            "user1", "testfirst", "testlast", "user_test@gmail.com", "password")
        user_test.id = 4000
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_email_signup(self):

        user_test = User.signup(
            "user3","testfirst", "testlast", None, "password" )

        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()


    def test_invalid_first_name_signup(self):

        user_test = User.signup(
            "user3","user_test@gmail.com", None, "testlast", "password" )

        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()


    def test_invalid_last_name_signup(self):

        user_test = User.signup(
            "user3","user_test@gmail.com", "testfirst", None, "password" )

        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_password(self):

        with self.assertRaises(ValueError) as context:
            user_test = User.signup(
                "user3", "testfirst", "testlast", "user_test@gmail.com", "")

        with self.assertRaises(ValueError) as context:
            user_test = User.signup(
                "user3",  "testfirst", "testlast", "user_test@gmail.com", None)

    def test_valid_authentication(self):
        """test login method"""

        good_username = User.authenticate("user1", "password")
        self.assertEqual(self.user1, good_username)

    def test_invalid_password(self):
        self.assertFalse(User.authenticate("user1", "piggies"))

    def test_invalid_username(self):
        self.assertFalse(User.authenticate("user7", "password"))
