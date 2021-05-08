from pytest import MonkeyPatch

from flask_login import current_user

from rpiplatesrecognition.forms import AddPlateForm
from rpiplatesrecognition.models import Whitelist, User


def validate_ajax_form_error_response(error_response, expected_fields):
    assert 'errors' in error_response
    dict_ = error_response['errors']

    assert len(expected_fields) == len(dict_)
    assert all(field in dict_ for field in expected_fields)


def test_edit_whitelist_add_plate_returns_error_upon_wrong_plate(client, monkeypatch: MonkeyPatch):
    user = User.query.filter_by(username='user1').first()
    assert user

    monkeypatch.setattr('flask_login.current_user', user)

    whitelist = user.whitelists[0]
    assert whitelist
    submitted_form = AddPlateForm(plate='not_valid_plate', whitelist_id=whitelist.id)
