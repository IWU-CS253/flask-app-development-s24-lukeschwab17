import os
import app as flaskr
import unittest
import tempfile

class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, flaskr.app.config['DATABASE'] = tempfile.mkstemp()
        flaskr.app.testing = True
        self.app = flaskr.app.test_client()
        with flaskr.app.app_context():
            flaskr.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(flaskr.app.config['DATABASE'])

    def test_empty_db(self):
        rv = self.app.get('/')
        assert b'No entries here so far' in rv.data

    def test_messages(self):
        rv = self.app.post('/add', data=dict(
            title='<Hello>',
            text='<strong>HTML</strong> allowed here',
            category='A category'
        ), follow_redirects=True)
        assert b'No entries here so far' not in rv.data
        assert b'&lt;Hello&gt;' in rv.data
        assert b'<strong>HTML</strong> allowed here' in rv.data
        assert b'A category' in rv.data

    def test_deletion(self):
        # add post
        rv = self.app.post('/add', data=dict(
            title='<Hello>',
            text='<strong>HTML</strong> allowed here',
            category='A category'
        ), follow_redirects=True)

        # delete it
        rv = self.app.post('/delete', data=dict(
            delete='1'
        ), follow_redirects=False)

        # redirect manually to '/', because in flask we use request.referrer
        # since we want deletion possible from filtered or non-filtered page
        rv = self.app.get('/')

        assert b'No entries here so far' in rv.data

    def test_edit(self):
        # create post
        rv = self.app.post('/add', data=dict(
            title='Test title',
            text='Test text',
            category='A category'
        ), follow_redirects=True)

        # move to edit page
        rv = self.app.post('/edit', data=dict(
            edit='1'
        ), follow_redirects=True)

        # edit post
        rv = self.app.post('/edit-success', data=dict(
            title='New title',
            text='New text',
            category='New category',
            id='1'
        ), follow_redirects=True)

        assert b'Test title' not in rv.data
        assert b'Test text' not in rv.data
        assert b'Test category' not in rv.data

        assert b'New title' in rv.data
        assert b'New text' in rv.data
        assert b'New category' in rv.data
    def test_edit_cancel(self):
        # create post
        rv = self.app.post('/add', data=dict(
            title='Test title',
            text='Test text',
            category='A category',
            id='1'
        ), follow_redirects=True)

        # move to edit page
        rv = self.app.post('/edit', data=dict(
            edit='1'
        ), follow_redirects=True)


        # cancel edit
        rv = self.app.get('/')
        print(rv.data)
        assert b'Test title' in rv.data
        assert b'Test text' in rv.data
        assert b'A category' in rv.data

    def test_filter_entry(self):
        # add post
        rv = self.app.post('/add', data=dict(
            title='<Hello>',
            text='<strong>HTML</strong> allowed here',
            category='A category'
        ), follow_redirects=True)

        # add second post
        rv = self.app.post('/add', data=dict(
            title='<Hello>',
            text='<strong>HTML</strong> allowed here',
            category='Another category'
        ), follow_redirects=True)

        # filter posts
        rv = self.app.get('/filter?filter=Another%20category')

        assert b'Another category' in rv.data
        assert b'A category' not in rv.data

if __name__ == '__main__':
    unittest.main()