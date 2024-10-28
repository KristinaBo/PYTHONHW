import json
import pytest

from faker import Faker
fake = Faker()

from Helpers.sessions import Session
from pytest_steps import test_steps

session = Session()
teamId = '9012433021'

@pytest.fixture
def create_body_for_goal():
    with open('TestData/goal.json', 'r') as f:
        body = json.load(f)
    body['name'] =  f'Goal name {fake.name()}'
    return body

def test_get_goals():
    res = session.get(f'/team/{teamId}/goal')
    assert res.status_code == 200, f"Response code was:  {str(res.status_code)} and body: {res.text}"

@pytest.mark.parametrize('name, status', [(fake.last_name(), 200), ('', 200), ('李红：这是书。', 200)])
def test_create_goal(name, status):
    body = { "name": name }
    res = session.post(f'/team/{teamId}/goal', json=body)
    assert res.status_code == status, f"Response code was: {str(res.status_code)} and body: {res.text}"
    response_json = res.json()
    assert response_json['goal']['name'] == name, f"Expected name: {name}, but got: {response_json['goal']['name']}"
    assert response_json['goal']['pretty_url'].endswith(response_json['goal']['pretty_id']), f"Expected pretty_url to end with pretty_id, but got: {response_json['goal']['pretty_url']}"

@test_steps('Create goal', 'Update goal')
def test_update_goal(create_body_for_goal):
    create_response = session.post(f'/team/{teamId}/goal', data=create_body_for_goal)
    goal_id = create_response.json()['goal']['id']
    yield

    upd_body = { "name": f'Goal updated {fake.name()}' }
    res = session.put(f'/goal/{goal_id}', data=upd_body)
    assert res.status_code == 200, f"Response code was:  {str(res.status_code)} and body: {res.text}"
    response_json = res.json()
    assert response_json['goal']['name'] == upd_body['name'], f"Expected name: {upd_body['name']}, but got: {response_json['goal']['name']}"
    assert response_json['goal']['pretty_url'].endswith(create_response.json()['goal']['pretty_id']), f"Expected pretty_url to end with pretty_id, but got: {response_json['goal']['pretty_url']}"
    assert response_json['goal']['date_updated'] is not None, "Expected date_updated to be not null"
    yield

@test_steps('Create goal', 'Get goal')
def test_get_goal(create_body_for_goal):
    create_response = session.post(f'/team/{teamId}/goal', data=create_body_for_goal)
    goal_id = create_response.json()['goal']['id']
    yield

    res = session.get(f'/goal/{goal_id}')
    assert res.status_code == 200, f"Response code was:  {str(res.status_code)} and body: {res.text}"
    response_json = res.json()
    assert response_json['goal']['name'] == create_response.json()['goal']['name'], f"Expected name: {create_response.json()['goal']['name']}, but got: {response_json['goal']['name']}"
    yield

@test_steps('Create goal', 'Delete goal', 'Get goal')
def test_get_goal(create_body_for_goal):
    create_response = session.post(f'/team/{teamId}/goal', data=create_body_for_goal)
    goal_id = create_response.json()['goal']['id']
    yield

    del_res = session.delete(f'/goal/{goal_id}')
    assert del_res.status_code == 200, f"Response code was:  {str(del_res.status_code)} and body: {del_res.text}"
    yield

    res = session.get(f'/goal/{goal_id}')
    assert res.status_code == 403, f"Response code was:  {str(res.status_code)} and body: {res.text}"
    yield

def test_create_key_result(create_body_for_goal):
    create_response = session.post(f'/team/{teamId}/goal', data=create_body_for_goal)
    goal_id = create_response.json()['goal']['id']

    url = f'/goal/{goal_id}/key_result'
    body = {
        "name": f'New Key Result Name {fake.name()}',
        "owners": [],
        "type": "number",
        "steps_start": 0,
        "steps_end": 10,
    }

    response = session.post(url, json=body)
    assert response.status_code == 200, f"Response code was:  {str(response.status_code)} and body: {response.text}"
    assert response.json()['key_result']['goal_id'] == goal_id, f"Expected goal_id: {goal_id}, but got: {response.json()['key_result']['goal_id']}"

