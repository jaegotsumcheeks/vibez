import unittest

from server import app
from model import db, connect_to_db, User, Playlist, Song, SongPlaylist
import re


class ServerTests(unittest.TestCase):
    """Tests for my Vibez site."""

    def setUp(self):
        self.client = app.test_client()
        app.config['TESTING'] = True

    def test_login(self):
        result = self.client.get("/")
        self.assertIn(
            b"Vibez", result.data)

    def test_register_page(self):
        result = self.client.get("/register")
        self.assertIn(b"Create New Account", result.data)


class TestUser(unittest.TestCase):
    """Ensure user can register"""


    def setUp(self):
        """Stuff to do before every test."""

        # Get the Flask test client
        self.client = app.test_client()

        # Show Flask errors that happen during tests
        app.config['TESTING'] = True

        # Connect to test database
        connect_to_db(app)

        # Create tables and add sample data
        db.create_all()
        jen = User(fname='Jennifer', lname='Kim', email='jy.kim8295@gmail.com', password='Elelelel91')
        db.session.add(jen)
        db.session.commit()
    
    def tearDown(self):
        """Do at end of every test."""

        db.session.close()
        db.drop_all()
    
    def test_user_registration(self):
        """Test to see if new user can be registered"""
        with self.client:
            response = self.client.post('/register', data={
                'fname': 'Jessica',
                'lname': 'Kim',    
                'email': 'jessica_yeon_kim@yahoo.com',
                'password': 'mushrooms'
            }, follow_redirects=True)
            self.assertIn(b'User Jessica has been added', response.data)
            user = User.query.filter_by(email = "jessica_yeon_kim@yahoo.com").first()
            self.assertTrue(str(user) == '<User user_id=2 email=jessica_yeon_kim@yahoo.com>')
    
    def test_existing_user_registration(self):
        """Test to see if existing user is not all"""
        with self.client:
            response = self.client.post('/register', data={
                'fname': 'Jennifer',
                'lname': 'Kim',
                'email': 'jy.kim8295@gmail.com',
                'password': 'Elelelel91'
                }, follow_redirects=True)
            self.assertIn(b'User already exists', response.data)



class FlaskTests(unittest.TestCase):
    """Flask tests for valid and invalid login credentials and successful logout session"""

    def setUp(self):
        """Stuff to do before every test."""

        # Get the Flask test client
        self.client = app.test_client()

        # Show Flask errors that happen during tests
        app.config['TESTING'] = True

        # Connect to test database
        connect_to_db(app)

        # Create tables and add sample data
        db.create_all()
        jen = User(fname = 'Jennifer',lname = 'Kim', email = 'jy.kim8295@gmail.com',password = 'Elelelel91')
        db.session.add(jen)
        db.session.commit()

    def tearDown(self):
        """Do at end of every test."""

        db.session.close()
        db.drop_all()
    

    def test_login_incorrect_email(self):
        #attempt login with incorrect email credentials
        response = self.client.post('/', data={
            'email': 'jy.kim@gmail.com',
            'password': 'Elelelel91'
        }, follow_redirects=True)
        self.assertTrue(re.search('No such user',
                        response.get_data(as_text=True)))
    

    
    def test_login_incorrect_password(self):
        #attempt login with incorrect password credentials
        response = self.client.post('/', data={
            'email': 'jy.kim8295@gmail.com',
            'password': 'Elelelel'
        }, follow_redirects=True)
        self.assertTrue(re.search('Incorrect password',
                                  response.get_data(as_text=True)))

    
    def test_login_correct_user(self):
        #attempt login with correct user credentials
        response = self.client.post('/', data={
            'email': 'jy.kim8295@gmail.com',
            'password': 'Elelelel91'
        }, follow_redirects=True)
        self.assertTrue(re.search('User has successfully logged in',
                                  response.get_data(as_text=True)))
    
    def test_logout(self):
        #attempt to logout
        with self.client:
            self.client.post('/', data={
                            'email': 'jy.kim8295@gmail.com',
                            'password': 'Elelelel91'
            }, follow_redirects=True)
        response = self.client.get('/logout', follow_redirects=True)
        self.assertTrue(re.search('Logged out.',
                                  response.get_data(as_text=True)))

#finish writing tests for session
class SessionTests(unittest.TestCase):
    """Check for successful session storage"""


    def setUp(self):
        self.client = app.test_client()
        app.config['TESTING'] = True

        with app.test_client() as c:
            with c.session_transaction() as sess:
                sess['a_key'] = 'a value'

    def tearDown(self):
        """Do at end of every test."""

        db.session.close()
        db.drop_all()
        
    def session(self):
        #check if session is stored after logging in
        with app.test_client() as c:
            rv = c.get('/')
            assert flask.session["user_id"] == 4


                                




    
  

if __name__ == "__main__":
    unittest.main()
