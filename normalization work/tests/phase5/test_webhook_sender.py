"""
Tests for Webhook Sender Module
"""

import json
import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Import webhook sender functions
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from src.phase5.webhook_sender import (
    load_webhook_config,
    build_webhook_payload,
    send_set_to_webhook,
    send_all_sets
)


# Fixtures
@pytest.fixture
def mock_config():
    """Mock webhook configuration."""
    return {
        'webhook_url': 'https://test.example.com/api/render',
        'access_key': 'test-key-123',
        'timeout_seconds': 30,
        'retry_attempts': 3,
        'retry_delay_seconds': 1
    }


@pytest.fixture
def sample_set():
    """Sample Phase 5 set data."""
    return {
        'SetNumber': 1,
        'SetNoWrite': 'One',
        'SetLabel': 'Set 1 of 2',
        'Template': 'SROGsMaster.docx',
        'OutputName': 'John Doe vs ABC Corp - Discovery Propounded SROGs Set 1 of 2',
        'HeadOfHousehold': 'John Doe',
        'TargetDefendant': 'ABC Corp',
        'HasMold': True,
        'HasVermin': True,
        'IsManager': True
    }


@pytest.fixture
def sample_phase5_output():
    """Sample Phase 5 output structure."""
    return {
        'datasets': [
            {
                'doc_type': 'SROGs',
                'sets': [
                    {
                        'Template': 'SROGsMaster.docx',
                        'OutputName': 'John Doe vs ABC Corp - SROGs Set 1 of 2',
                        'SetNumber': 1,
                        'HasMold': True
                    },
                    {
                        'Template': 'SROGsMaster.docx',
                        'OutputName': 'John Doe vs ABC Corp - SROGs Set 2 of 2',
                        'SetNumber': 2,
                        'HasVermin': True
                    }
                ]
            }
        ]
    }


# Tests for load_webhook_config
def test_load_webhook_config_file_not_found():
    """Test loading config when file doesn't exist."""
    with pytest.raises(FileNotFoundError):
        load_webhook_config('nonexistent_config.json')


def test_load_webhook_config_missing_required_field(tmp_path):
    """Test loading config with missing required fields."""
    config_file = tmp_path / "bad_config.json"
    config_file.write_text(json.dumps({'webhook_url': 'http://test.com'}))

    with pytest.raises(ValueError, match="Missing required config field: access_key"):
        load_webhook_config(str(config_file))


def test_load_webhook_config_valid(tmp_path):
    """Test loading valid config file."""
    config_file = tmp_path / "config.json"
    config_data = {
        'webhook_url': 'http://test.com',
        'access_key': 'key123'
    }
    config_file.write_text(json.dumps(config_data))

    result = load_webhook_config(str(config_file))

    assert result['webhook_url'] == 'http://test.com'
    assert result['access_key'] == 'key123'


# Tests for build_webhook_payload
def test_build_webhook_payload_structure(sample_set):
    """Test webhook payload has correct structure."""
    payload = build_webhook_payload(sample_set, 'test-key')

    assert 'data' in payload
    assert 'accessKey' in payload
    assert 'templateName' in payload
    assert 'outputName' in payload


def test_build_webhook_payload_values(sample_set):
    """Test webhook payload contains correct values."""
    payload = build_webhook_payload(sample_set, 'test-key-123')

    assert payload['accessKey'] == 'test-key-123'
    assert payload['templateName'] == 'SROGsMaster.docx'
    assert payload['outputName'] == 'John Doe vs ABC Corp - Discovery Propounded SROGs Set 1 of 2'
    assert payload['data'] == sample_set


def test_build_webhook_payload_data_includes_all_fields(sample_set):
    """Test that data field includes all original set fields."""
    payload = build_webhook_payload(sample_set, 'test-key')

    assert payload['data']['HasMold'] is True
    assert payload['data']['HasVermin'] is True
    assert payload['data']['IsManager'] is True
    assert payload['data']['SetNumber'] == 1


# Tests for send_set_to_webhook
@patch('src.phase5.webhook_sender.requests.post')
def test_send_set_to_webhook_success(mock_post, sample_set, mock_config):
    """Test successful webhook send."""
    # Mock successful response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'status': 'success'}
    mock_post.return_value = mock_response

    result = send_set_to_webhook(sample_set, mock_config)

    assert result['success'] is True
    assert result['status_code'] == 200
    assert result['attempts'] == 1
    assert mock_post.called


@patch('src.phase5.webhook_sender.requests.post')
def test_send_set_to_webhook_http_error(mock_post, sample_set, mock_config):
    """Test webhook send with HTTP error."""
    # Mock error response (no retries for this test)
    mock_response = Mock()
    mock_response.status_code = 500
    mock_response.text = 'Internal Server Error'
    mock_post.return_value = mock_response

    # Set max attempts to 1 to avoid retries
    mock_config['retry_attempts'] = 1

    result = send_set_to_webhook(sample_set, mock_config)

    assert result['success'] is False
    assert result['status_code'] == 500
    assert 'HTTP 500' in result['error']


@patch('src.phase5.webhook_sender.requests.post')
def test_send_set_to_webhook_timeout(mock_post, sample_set, mock_config):
    """Test webhook send with timeout."""
    import requests
    mock_post.side_effect = requests.exceptions.Timeout()

    # Set max attempts to 1 to avoid retries
    mock_config['retry_attempts'] = 1

    result = send_set_to_webhook(sample_set, mock_config)

    assert result['success'] is False
    assert 'timeout' in result['error'].lower()


@patch('src.phase5.webhook_sender.requests.post')
@patch('src.phase5.webhook_sender.time.sleep')
def test_send_set_to_webhook_retry_success(mock_sleep, mock_post, sample_set, mock_config):
    """Test webhook send succeeds after retry."""
    # First call fails, second succeeds
    mock_response_fail = Mock()
    mock_response_fail.status_code = 503
    mock_response_fail.text = 'Service Unavailable'

    mock_response_success = Mock()
    mock_response_success.status_code = 200
    mock_response_success.json.return_value = {'status': 'success'}

    mock_post.side_effect = [mock_response_fail, mock_response_success]

    result = send_set_to_webhook(sample_set, mock_config)

    assert result['success'] is True
    assert result['attempts'] == 2
    assert mock_sleep.called


@patch('src.phase5.webhook_sender.requests.post')
def test_send_set_to_webhook_request_exception(mock_post, sample_set, mock_config):
    """Test webhook send with request exception."""
    import requests
    mock_post.side_effect = requests.exceptions.RequestException("Connection error")

    mock_config['retry_attempts'] = 1

    result = send_set_to_webhook(sample_set, mock_config)

    assert result['success'] is False
    assert 'Request error' in result['error']


@patch('src.phase5.webhook_sender.requests.post')
def test_send_set_to_webhook_non_json_response(mock_post, sample_set, mock_config):
    """Test webhook send with non-JSON response (e.g., binary document)."""
    # Mock response that returns 200 but non-JSON content (like a Word document)
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.content = b'Binary document content...'
    mock_response.text = 'Binary document content...'
    mock_response.headers = {'Content-Type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'}
    mock_response.json.side_effect = json.JSONDecodeError("Expecting value", "", 0)
    mock_post.return_value = mock_response

    result = send_set_to_webhook(sample_set, mock_config)

    # Should still be successful since status code is 200
    assert result['success'] is True
    assert result['status_code'] == 200
    assert result['attempts'] == 1
    assert 'response' in result
    # Response should contain metadata about the non-JSON response
    assert result['response']['content_type'] == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    assert result['response']['content_length'] > 0


# Tests for send_all_sets
@patch('src.phase5.webhook_sender.send_set_to_webhook')
def test_send_all_sets_counts(mock_send, sample_phase5_output, mock_config):
    """Test send_all_sets processes correct number of sets."""
    # Mock all sends as successful
    mock_send.return_value = {'success': True, 'status_code': 200, 'attempts': 1}

    summary = send_all_sets(sample_phase5_output, mock_config, verbose=False)

    assert summary['total_sets'] == 2
    assert summary['succeeded'] == 2
    assert summary['failed'] == 0
    assert mock_send.call_count == 2


@patch('src.phase5.webhook_sender.send_set_to_webhook')
def test_send_all_sets_with_failures(mock_send, sample_phase5_output, mock_config):
    """Test send_all_sets handles failures correctly."""
    # First succeeds, second fails
    mock_send.side_effect = [
        {'success': True, 'status_code': 200, 'attempts': 1},
        {'success': False, 'error': 'Failed', 'attempts': 3}
    ]

    summary = send_all_sets(sample_phase5_output, mock_config, verbose=False)

    assert summary['total_sets'] == 2
    assert summary['succeeded'] == 1
    assert summary['failed'] == 1


@patch('src.phase5.webhook_sender.send_set_to_webhook')
def test_send_all_sets_results_list(mock_send, sample_phase5_output, mock_config):
    """Test send_all_sets returns list of results."""
    mock_send.return_value = {'success': True, 'status_code': 200, 'attempts': 1}

    summary = send_all_sets(sample_phase5_output, mock_config, verbose=False)

    assert 'results' in summary
    assert len(summary['results']) == 2
    assert all('set_name' in r for r in summary['results'])


@patch('src.phase5.webhook_sender.send_set_to_webhook')
def test_send_all_sets_empty_datasets(mock_send, mock_config):
    """Test send_all_sets with empty datasets."""
    empty_output = {'datasets': []}

    summary = send_all_sets(empty_output, mock_config, verbose=False)

    assert summary['total_sets'] == 0
    assert summary['succeeded'] == 0
    assert summary['failed'] == 0
    assert not mock_send.called


# Integration-style test
@patch('src.phase5.webhook_sender.requests.post')
def test_full_workflow(mock_post, sample_phase5_output, mock_config):
    """Test complete workflow from Phase 5 output to webhook."""
    # Mock successful responses
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'status': 'success'}
    mock_post.return_value = mock_response

    summary = send_all_sets(sample_phase5_output, mock_config, verbose=False)

    # Verify all sets were sent
    assert summary['total_sets'] == 2
    assert summary['succeeded'] == 2
    assert summary['failed'] == 0

    # Verify webhook was called correctly
    assert mock_post.call_count == 2

    # Check first call's payload structure
    first_call_args = mock_post.call_args_list[0]
    payload = first_call_args[1]['json']

    assert 'data' in payload
    assert 'accessKey' in payload
    assert 'templateName' in payload
    assert 'outputName' in payload
    assert payload['accessKey'] == mock_config['access_key']
