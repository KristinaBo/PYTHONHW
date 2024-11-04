import json
import pytest

from faker import Faker
fake = Faker()

from Helpers.sessions import Session
from pytest_steps import test_steps

session = Session()
taskId = '8696gdd0b'
taskUrl = f'/task/{taskId}/comment'

@pytest.fixture
def create_body_for_task_comment():
    with open('TestData/taskComment.json', 'r') as f:
        body = json.load(f)
    body['comment_text'] = f'task_comment text {fake.name()}'
    return body

def test_get_task_comments():
    res = session.get(taskUrl)
    assert res.status_code == 200, f"Response code was: {str(res.status_code)} and body: {res.text}"

@pytest.mark.parametrize('name, status', [(fake.last_name(), 200), ('', 401)])
def test_create_task_comment(name, status):
    body = { "comment_text": name }
    res = session.post(taskUrl, json=body)

    assert res.status_code == status, f"Response code was: {str(res.status_code)} and body: {res.text}"

def test_create_task_comment_with_custom_task_id():
    body = { "comment_text": 'custom' }
    query = { 'team_id':9012433021, 'custom_task_ids':True, }
    res = session.post(taskUrl, params=query, json=body)

    assert res.status_code == 200, f"Response code was: {str(res.status_code)} and body: {res.text}"

@test_steps('Create task_comment', 'Update task_comment')
def test_update_task_comment(create_body_for_task_comment):
    create_response = session.post(taskUrl, json=create_body_for_task_comment)
    task_comment_id = create_response.json()['id']
    yield

    upd_body = { "comment_text": f'task_comment updated {fake.name()}' }
    res = session.put(f'/comment/{task_comment_id}', json=upd_body)
    assert res.status_code == 200, f"Response code was: {str(res.status_code)} and body: {res.text}"
    yield


@test_steps('Create task_comment', 'Delete task_comment')
def test_delete_task_comment(create_body_for_task_comment):
    create_response = session.post(taskUrl, json=create_body_for_task_comment)
    task_comment_id = create_response.json()['id']
    yield

    del_res = session.delete(f'/comment/{task_comment_id}')
    assert del_res.status_code == 200, f"Response code was: {str(del_res.status_code)} and body: {del_res.text}"
    yield

