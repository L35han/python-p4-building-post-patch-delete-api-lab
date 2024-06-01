import pytest
from datetime import datetime
from app import app, db, Message, Bakery, BakedGood

@pytest.fixture(scope='module')
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'

    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.drop_all()

@pytest.fixture(scope='module')
def init_database():
    with app.app_context():
        # Create a test message
        message = Message(body="Test message", username="test_user")
        db.session.add(message)
        db.session.commit()

class TestApp:
    '''Flask application tests'''

    @pytest.fixture(autouse=True)
    def setup_and_cleanup(self, client):
        with app.app_context():
            db.create_all()
            yield
            db.session.query(Message).delete()
            db.session.commit()
            db.drop_all()

    def test_creates_baked_goods(self):
        '''can POST new baked goods through "/baked_goods" route.'''
        with app.app_context():
            af = BakedGood.query.filter_by(name="Apple Fritter").first()
            if af:
                db.session.delete(af)
                db.session.commit()

            response = app.test_client().post(
                '/baked_goods',
                json={
                    "name": "Apple Fritter",
                    "bakery_id": 1,
                }
            )

            af = BakedGood.query.filter_by(name="Apple Fritter").first()

            assert response.status_code == 201
            assert response.content_type == 'application/json'
            assert af.id

    def test_updates_bakeries(self):
        '''can PATCH bakeries through "bakeries/<int:id>" route.'''
        with app.app_context():
            mb = Bakery.query.filter_by(id=1).first()
            if not mb:
                mb = Bakery(id=1, name="Test Bakery")
                db.session.add(mb)
                db.session.commit()

            response = app.test_client().patch(
                '/bakeries/1',
                json = {
                    "name": "Your Bakery",
                }
            )

            assert response.status_code == 200
            assert response.content_type == 'application/json'
            assert mb.name == "Your Bakery"

    def test_deletes_baked_goods(self):
        '''can DELETE baked goods through "baked_goods/<int:id>" route.'''
        with app.app_context():
            af = BakedGood.query.filter_by(name="Apple Fritter").first()
            if not af:
                af = BakedGood(
                    name="Apple Fritter",
                    bakery_id=1,
                )
                db.session.add(af)
                db.session.commit()

            response = app.test_client().delete(
                f'/baked_goods/{af.id}'
            )

            assert response.status_code == 200
            assert response.content_type == 'application/json'
            assert not BakedGood.query.filter_by(name="Apple Fritter").first()

    def test_has_correct_columns(self, client):
        with app.app_context():
            hello_from_liza = Message(body="Hello 👋", username="Liza")
            db.session.add(hello_from_liza)
            db.session.commit()

            assert hello_from_liza.body == "Hello 👋"
            assert hello_from_liza.username == "Liza"
            assert isinstance(hello_from_liza.created_at, datetime)

            db.session.delete(hello_from_liza)
            db.session.commit()

    def test_returns_list_of_json_objects_for_all_messages_in_database(self, client):
        '''returns a list of JSON objects for all messages in the database.'''
        with app.app_context():
            response = client.get('/messages')
            records = Message.query.all()

            for message in response.json:
                assert message['id'] in [record.id for record in records]
                assert message['body'] in [record.body for record in records]

    def test_creates_new_message_in_the_database(self, client):
        '''creates a new message in the database.'''
        with app.app_context():
            client.post('/messages', json={"body": "Hello 👋", "username": "Liza"})
            h = Message.query.filter_by(body="Hello 👋").first()
            assert h

            db.session.delete(h)
            db.session.commit()

    def test_returns_data_for_newly_created_message_as_json(self, client):
        '''returns data for the newly created message as JSON.'''
        with app.app_context():
            response = client.post('/')
